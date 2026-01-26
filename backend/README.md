# Paradox Network Application - Backend

## Overview

The Paradox Network Application (PNA) backend implements a revolutionary messaging platform that transmits **semantic meaning (latent vectors)** instead of raw data, enabling:

- **99% bandwidth reduction** vs traditional messaging
- **Zero-cost receiving** through Ethio Telecom partnership
- **Works in 2G/EDGE** networks
- **Dual-lane traffic architecture** (zero-rated + normal internet)

## Architecture

### Dual-Lane Traffic System

**Lane A (Zero-Rated)** - `core.pna.et`:
- Core messaging (send/receive)
- Subscription validation
- Emergency broadcasts
- **FREE** for Ethio Telecom subscribers

**Lane B (Normal Internet)** - `api.pna.et`:
- App updates
- Analytics (opt-in)
- External integrations
- Uses user's normal data plan

### Technology Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 15 + Redis
- **Vector Storage**: Pinecone (planned)
- **AI/ML**: ParadoxLF + CLIP
- **Protocol**: PTP (Paradox Transport Protocol)

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**:
```bash
cd c:\Users\fitsum.DESKTOP-JDUVJ6V\Downloads\paradoxapp\backend
```

2. **Create environment file**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

4. **Access the API**:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Traffic Stats: http://localhost:8000/traffic/stats

### Development Setup (Without Docker)

1. **Create virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start PostgreSQL and Redis** (or use Docker for just databases):
```bash
docker-compose up postgres redis -d
```

4. **Run the application**:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication (`/v1/auth`)

- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login
- `POST /v1/auth/refresh` - Refresh token
- `GET /v1/auth/me` - Get current user

### Messaging (`/v1/messages`)

- `POST /v1/messages/send` - Send message (2-5 KB)
- `POST /v1/messages/send/image` - Send image (3-4 KB vs 2-10 MB!)
- `GET /v1/messages/receive` - Receive messages (zero-rated)
- `GET /v1/messages/history/{contact_id}` - Message history
- `POST /v1/messages/read/{message_id}` - Mark as read
- `GET /v1/messages/stats` - Bandwidth statistics

### Subscription (`/v1/subscription`)

- `GET /v1/subscription/status` - Current subscription
- `POST /v1/subscription/purchase` - Purchase subscription
- `POST /v1/subscription/cancel` - Cancel auto-renewal
- `GET /v1/subscription/plans` - Available plans

## Core Components

### 1. Traffic Router (`app/core/traffic_router.py`)

Enforces strict separation between zero-rated and normal traffic:

```python
from app.core.traffic_router import traffic_router

# Enforce zero-rated routing
traffic_router.enforce_traffic_separation(
    domain="core.pna.et",
    operation="message_send"
)
```

### 2. PTP Protocol (`app/services/ptp_protocol.py`)

Compresses 512D vectors to 1-4 KB:

```python
from app.services.ptp_protocol import ptp_protocol, PTPMessage

# Create message
msg = PTPMessage(
    sender_id="user123",
    receiver_id="user456",
    latent_vector=vector,
    intent_type="textual"
)

# Serialize and compress
compressed = ptp_protocol.serialize_message(msg)
print(f"Compressed size: {len(compressed)} bytes")  # ~2-4 KB
```

### 3. Latent Encoder (`app/services/latent_encoder.py`)

Encodes content to semantic vectors:

```python
from app.services.latent_encoder import latent_encoder

# Encode text
vector = latent_encoder.encode_text("Hello, how are you?")

# Encode image
vector = latent_encoder.encode_image("photo.jpg")
```

### 4. Latent Decoder (`app/services/latent_decoder.py`)

Reconstructs content from vectors:

```python
from app.services.latent_decoder import latent_decoder

# Decode text
text = latent_decoder.decode_text(vector)

# Decode image
image_bytes = latent_decoder.decode_image(vector)
```

## Bandwidth Savings

| Content Type | Traditional Size | PNA Size | Savings |
|--------------|-----------------|----------|---------|
| Text Message | 1-2 KB | 1-2 KB | ~0% |
| Image | 2-10 MB | 3-4 KB | **99.9%** |
| Voice (planned) | 1-5 MB | 2-3 KB | **99.9%** |

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ptp_protocol.py

# Run with coverage
pytest --cov=app tests/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZERO_RATED_DOMAIN` | Zero-rated domain | `core.pna.et` |
| `NORMAL_DOMAIN` | Normal internet domain | `api.pna.et` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing key | - |
| `ZERO_RATING_ENABLED` | Enable zero-rating | `True` |
| `TELECOM_PARTNER` | Telecom partner | `ethio_telecom` |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration
│   ├── core/
│   │   ├── traffic_router.py  # Dual-lane routing
│   │   └── security.py        # Auth & encryption
│   ├── models/
│   │   ├── user.py
│   │   ├── message.py
│   │   └── subscription.py
│   ├── services/
│   │   ├── ptp_protocol.py    # PTP implementation
│   │   ├── latent_encoder.py  # Vector encoding
│   │   └── latent_decoder.py  # Vector decoding
│   └── api/
│       └── v1/
│           ├── auth.py
│           ├── messages.py
│           └── subscription.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Deployment

### Staging

```bash
# Build image
docker build -t pna-backend:staging .

# Run container
docker run -p 8000:8000 --env-file .env pna-backend:staging
```

### Production

See deployment guide in `/docs/DEPLOYMENT.md`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

[To be determined]

## Contact

For questions or support, please contact the development team.

---

**Status**: MVP Implementation Phase  
**Last Updated**: 2026-01-26
