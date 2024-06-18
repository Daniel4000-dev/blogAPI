import motor.motor_asyncio
from dotenv import load_dotenv
from typing import Any

from bson import ObjectId
from pydantic_core import core_schema

from pydantic import BaseModel, Field, EmailStr 
import os

import certifi

#load env
load_dotenv()

# Retrieve the MongoDB URL from environment variables
mongodb_url = os.getenv("MONGODB_URL")

# Ensure that the MongoDB URL is not None
if mongodb_url is None:
    raise ValueError("MONGODB_URL environment variable not set")

# Set up MongoDB client with SSL certificates
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url, tlsCAFile=certifi.where())

db = client.blog_api

#BSON and fastapi JSON
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectID")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )
    
    @classmethod
    def __allow_population_by_field_name__(cls, field_name):
        return True

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    
    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com",
                "password": "secret_code"
            }
        }
        
        
class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    
    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com",
            }
        }