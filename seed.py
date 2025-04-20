from app import create_app, db
from app.models import User, Job, Review
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        # Create test users
        client = User(
            email='client@example.com',
            phone_number='+254700000000',
            role='client',
            is_verified=True
        )
        client.set_password('password123')

        personnel = User(
            email='personnel@example.com',
            phone_number='+254700000001',
            role='personnel',
            is_verified=True
        )
        personnel.set_password('password123')

        db.session.add(client)
        db.session.add(personnel)
        db.session.commit()

        # Create test jobs
        jobs = [
            Job(
                title='Bathroom Renovation',
                description='Need to renovate a small bathroom, including new tiles and fixtures',
                service_type='plumbing',
                duration_days=14,
                budget=50000,
                status='open',
                client_id=client.id,
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            Job(
                title='Kitchen Wiring',
                description='Install new electrical outlets and lighting in kitchen',
                service_type='electrical',
                duration_days=7,
                budget=25000,
                status='open',
                client_id=client.id,
                created_at=datetime.utcnow()
            )
        ]

        for job in jobs:
            db.session.add(job)
        
        db.session.commit()

        # Create test review
        review = Review(
            rating=5,
            comment='Excellent work, very professional',
            reviewer_id=client.id,
            reviewee_id=personnel.id,
            job_id=jobs[0].id
        )

        db.session.add(review)
        db.session.commit()

        print('Database seeded successfully!')

if __name__ == '__main__':
    seed_database()