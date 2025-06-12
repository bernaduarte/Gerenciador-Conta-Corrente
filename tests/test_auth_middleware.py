import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from app.utils.auth_middleware import require_auth
import jwt
from app.config import SECRET_KEY, ALGORITHM

@pytest.fixture
def mock_request():
    request = Mock()
    request.cookies = {}
    request.state = Mock()
    return request

def test_require_auth_no_token(mock_request):
    with pytest.raises(HTTPException) as exc_info:
        require_auth(mock_request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Redirect"

def test_require_auth_expired_token(mock_request):
    expired_payload = {"sub": "test_user", "exp": 0} 
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    mock_request.cookies = {"access_token": expired_token}

    with pytest.raises(HTTPException) as exc_info:
        require_auth(mock_request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expirado"

def test_require_auth_invalid_token(mock_request):
    invalid_token = "invalid.token.string"
    mock_request.cookies = {"access_token": invalid_token}

    with pytest.raises(HTTPException) as exc_info:
        require_auth(mock_request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido"

def test_require_auth_valid_token(mock_request):
    valid_payload = {"sub": "test_user", "user_type": "NORMAL"}
    valid_token = jwt.encode(valid_payload, SECRET_KEY, algorithm=ALGORITHM)
    mock_request.cookies = {"access_token": valid_token}

    require_auth(mock_request)
    assert mock_request.state.user == valid_payload