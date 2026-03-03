"""
Firebase Admin SDK setup and database abstraction layer.
Handles Firestore and Realtime Database operations with robust error handling.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
import firebase_admin
from firebase_admin import credentials, firestore, db
from firebase_admin.exceptions import FirebaseError

from config import config

logger = logging.getLogger(__name__)


class FirebaseManager:
    """Singleton manager for Firebase operations"""
    
    _instance: Optional['FirebaseManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._app = None
            self._firestore