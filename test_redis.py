#!/usr/bin/env python3
"""
Simple Redis connection test script
Run this to verify Redis is working before starting Django
"""

import redis
import sys

def test_redis_connection():
    """Test Redis connection"""
    try:
        # Create Redis client
        r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✅ Redis read/write test successful: {value.decode()}")
        
        # Clean up
        r.delete('test_key')
        print("✅ Redis cleanup successful!")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("Make sure Redis server is running on 127.0.0.1:6379")
        return False
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Redis connection...")
    success = test_redis_connection()
    
    if success:
        print("\n🎉 Redis is ready! You can now start Django with WebSocket support.")
        sys.exit(0)
    else:
        print("\n💥 Redis setup failed. Please fix the issues above.")
        sys.exit(1)









