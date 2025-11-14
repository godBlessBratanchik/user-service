import asyncio
from .kafka import KafkaConsumerManager, TOPIC_USERS_REGISTERED, KAFKA_ENABLED
from .db import get_session
from .repository import ProfileRepo
from .schemas import ProfileCreate

async def handle_user_registered(message: dict):
    user_id = message.get("user_id")
    full_name = message.get("full_name", "")
    email = message.get("email", "")

    print(f"← Received event: UserRegistered")
    print(f"  User ID: {user_id}, Email: {email}")

    async for session in get_session():
        try:
            repo = ProfileRepo(session)
            profile_data = ProfileCreate(
                user_id=user_id,
                full_name=full_name,
                email=email
            )
            await repo.upsert(profile_data, user_id)
            print(f"✓ Profile created for user {user_id}")
        except Exception as e:
            print(f"✗ Error creating profile: {e}")
        finally:
            break

async def start_consumers():
    if not KAFKA_ENABLED:
        print("⊘ Kafka consumers disabled")
        return

    users_consumer = KafkaConsumerManager(
        topic=TOPIC_USERS_REGISTERED,
        group_id="profile-service-users"
    )

    await users_consumer.start()

    async def consume_loop():
        try:
            if users_consumer.consumer:
                async for record in users_consumer.consumer:
                    await handle_user_registered(record.value)
        except asyncio.CancelledError:
            print("Consumer loop cancelled")
        finally:
            await users_consumer.stop()

    asyncio.create_task(consume_loop())
