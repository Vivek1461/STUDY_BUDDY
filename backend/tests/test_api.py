"""Realistic API-level regression tests using an isolated SQLite database."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.config import get_settings

class StudyBuddyAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                                   poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)
        cls.temp = tempfile.TemporaryDirectory()
        get_settings().upload_dir = Path(cls.temp.name) / "uploads"
        get_settings().chroma_persist_dir = Path(cls.temp.name) / "chroma"
        def override_db():
            db = cls.Session()
            try:
                yield db
            finally:
                db.close()
        app.dependency_overrides[get_db] = override_db
        cls.override = override_db

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.temp.cleanup()
        cls.engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def register_and_login(self, email="learner@example.com"):
        response = self.client.post("/api/auth/register",
                                    json={"email": email, "password": "CorrectHorseBattery1"})
        self.assertEqual(response.status_code, 201, response.text)
        login = self.client.post("/api/auth/login",
                                 json={"email": email, "password": "CorrectHorseBattery1"})
        self.assertEqual(login.status_code, 200, login.text)
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    def test_health_endpoints_are_available(self):
        self.assertEqual(self.client.get("/health/live").json()["status"], "ok")
        self.assertEqual(self.client.get("/health/ready").status_code, 200)

    def test_register_login_and_duplicate_registration(self):
        headers = self.register_and_login()
        self.assertIn("Bearer", headers["Authorization"])
        duplicate = self.client.post("/api/auth/register",
                                     json={"email": "learner@example.com", "password": "CorrectHorseBattery1"})
        self.assertEqual(duplicate.status_code, 409)

    def test_invalid_login_does_not_reveal_account_existence(self):
        response = self.client.post("/api/auth/login",
                                    json={"email": "unknown@example.com", "password": "wrong-password"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Incorrect email or password")

    def test_guest_can_access_only_its_own_session(self):
        guest = self.client.post("/api/auth/guest")
        self.assertEqual(guest.status_code, 201)
        headers = {"Authorization": f"Bearer {guest.json()['access_token']}"}
        session = self.client.get("/api/sessions/" + guest.json()["session_id"], headers=headers)
        self.assertEqual(session.status_code, 200)
        self.assertTrue(session.json()["is_guest"])
        self.assertEqual(self.client.get("/api/sessions/" + guest.json()["session_id"]).status_code, 401)

    def test_user_cannot_read_another_users_session(self):
        owner_headers = self.register_and_login("owner@example.com")
        other_headers = self.register_and_login("other@example.com")
        guest = self.client.post("/api/auth/guest")
        guest_headers = {"Authorization": f"Bearer {guest.json()['access_token']}"}
        forbidden = self.client.get("/api/sessions/" + guest.json()["session_id"], headers=owner_headers)
        self.assertEqual(forbidden.status_code, 404)
        self.assertEqual(self.client.get("/api/sessions", headers=other_headers).json(), [])

    def test_protected_routes_reject_missing_and_invalid_tokens(self):
        no_auth = self.client.get("/api/sessions")
        bad_auth = self.client.get("/api/sessions", headers={"Authorization": "Bearer not-a-token"})
        self.assertEqual(no_auth.status_code, 401)
        self.assertEqual(bad_auth.status_code, 401)

    def test_chat_requires_uploaded_study_material(self):
        guest = self.client.post("/api/auth/guest").json()
        headers = {"Authorization": f"Bearer {guest['access_token']}"}
        response = self.client.post(f"/api/chat/{guest['session_id']}/messages",
                                    headers=headers, json={"message": "Explain this chapter"})
        self.assertEqual(response.status_code, 409)

    def test_upload_rejects_unsupported_file_before_writing(self):
        headers = self.register_and_login()
        response = self.client.post("/api/upload", headers=headers,
                                    files={"file": ("payload.exe", b"bad", "application/octet-stream")})
        self.assertEqual(response.status_code, 400)

    def test_upload_rejects_empty_document(self):
        headers = self.register_and_login()
        guest = self.client.post("/api/auth/guest").json()
        guest_headers = {"Authorization": f"Bearer {guest['access_token']}"}
        response = self.client.post("/api/upload", headers=guest_headers,
                                    data={"session_id": guest["session_id"]},
                                    files={"file": ("empty.txt", b"", "text/plain")})
        self.assertEqual(response.status_code, 400)

    def test_upload_and_index_successful_document(self):
        guest = self.client.post("/api/auth/guest").json()
        headers = {"Authorization": f"Bearer {guest['access_token']}"}
        with patch("app.routers.upload.extract_text", return_value="This is a test chapter about biology."), \
             patch("app.routers.upload.index_document", return_value=2):
            response = self.client.post("/api/upload", headers=headers,
                                        data={"session_id": guest["session_id"]},
                                        files={"file": ("biology.txt", b"Cell biology notes", "text/plain")})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["file"]["status"], "ready")
        self.assertEqual(response.json()["file"]["chunk_count"], 2)

    def test_upload_cannot_target_another_guest_session(self):
        first = self.client.post("/api/auth/guest").json()
        second = self.client.post("/api/auth/guest").json()
        headers = {"Authorization": f"Bearer {first['access_token']}"}
        response = self.client.post("/api/upload", headers=headers,
                                    data={"session_id": second["session_id"]},
                                    files={"file": ("notes.txt", b"notes", "text/plain")})
        self.assertEqual(response.status_code, 404)

    def test_realistic_upload_then_streaming_chat_and_history_persistence(self):
        guest = self.client.post("/api/auth/guest").json()
        headers = {"Authorization": f"Bearer {guest['access_token']}"}
        with patch("app.routers.upload.extract_text", return_value="Mitochondria produce cellular energy."), \
             patch("app.routers.upload.index_document", return_value=1):
            uploaded = self.client.post("/api/upload", headers=headers,
                                        data={"session_id": guest["session_id"]},
                                        files={"file": ("cell-biology.txt", b"study notes", "text/plain")})
        self.assertEqual(uploaded.status_code, 201, uploaded.text)
        with patch("app.routers.chat.retrieve_context", return_value=[
                {"text": "Mitochondria produce cellular energy.", "file_name": "cell-biology.txt"}]), \
             patch("app.routers.chat.stream_response", return_value=iter(["Mitochondria ", "produce energy."])):
            chat = self.client.post(f"/api/chat/{guest['session_id']}/messages",
                                    headers=headers, json={"message": "What do mitochondria do?"})
        self.assertEqual(chat.status_code, 200, chat.text)
        self.assertIn('"token": "Mitochondria "', chat.text)
        self.assertIn('"done": true', chat.text)
        db = self.Session()
        try:
            history = db.query(__import__("app.models", fromlist=["Message"]).Message).filter_by(
                session_id=guest["session_id"]).order_by(
                __import__("app.models", fromlist=["Message"]).Message.created_at).all()
            self.assertEqual([item.role for item in history], ["user", "assistant"])
            self.assertIn("produce energy", history[-1].content)
        finally:
            db.close()

    def test_failed_document_processing_rolls_back_file_record_and_disk_file(self):
        guest = self.client.post("/api/auth/guest").json()
        headers = {"Authorization": f"Bearer {guest['access_token']}"}
        with patch("app.routers.upload.extract_text", side_effect=ValueError("parser failure")):
            response = self.client.post("/api/upload", headers=headers,
                                        data={"session_id": guest["session_id"]},
                                        files={"file": ("broken.txt", b"not parseable", "text/plain")})
        self.assertEqual(response.status_code, 422)
        db = self.Session()
        try:
            from app.models import UploadFile
            self.assertEqual(db.query(UploadFile).count(), 0)
        finally:
            db.close()
        self.assertEqual(list(get_settings().upload_dir.glob("*.txt")), [])

    def test_user_can_upload_to_new_owned_session_without_session_id(self):
        headers = self.register_and_login("new-session@example.com")
        with patch("app.routers.upload.extract_text", return_value="A short set of notes."), \
             patch("app.routers.upload.index_document", return_value=1):
            response = self.client.post("/api/upload", headers=headers,
                                        files={"file": ("notes.txt", b"notes", "text/plain")})
        self.assertEqual(response.status_code, 201, response.text)
        listed = self.client.get("/api/sessions", headers=headers)
        self.assertEqual(len(listed.json()), 1)
        self.assertEqual(listed.json()[0]["id"], response.json()["session_id"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
