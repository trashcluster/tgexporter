# Telegram Data Exporter

A robust tool designed to programmatically export Telegram user data, including messages, media, and relational mapping between users and groups. It uses TDLib for high-performance interaction and PostgreSQL for persistent storage.

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- A Telegram account

## Setup Instructions

### 1. Get Telegram API Credentials

To interact with the Telegram API, you need to obtain an `API_ID` and `API_HASH`:

1.  Go to https://my.telegram.org and log in with your Telegram phone number.
2.  Click on **API development tools**.
3.  Fill out the form to create a new application. You can use any title and short name.
4.  Once the application is created, you will see your **App api_id** and **App api_hash**. Keep these private.

### 2. Configure Environment Variables

Create a file named `.env` in the root directory of the project and populate it with your credentials:

```env
API_ID=12345678
API_HASH=your_api_hash_string
PHONE=+1234567890
```

### 3. Run the Application

The application is designed to run in a Docker container.

#### Initial Run (Interactive Login)
The first time you run the app, you must perform an interactive login to authorize the session.

```bash
docker-compose run exporter
```

During this process, check your Telegram app for a login code and enter it into the terminal. If you have Two-Factor Authentication (2FA) enabled, you will also be prompted for your password.

#### Subsequent Runs (Automated)
Once the session is established, the session files are stored in the `./session` directory. Subsequent runs will be fully automated and can be started with:

```bash
docker-compose up
```

## Data Persistence

- **Database**: PostgreSQL data is stored in `./data/postgres`.
- **Sessions**: TDLib session files are stored in `./session`.
- **Downloads**: Photos, videos, and other media are stored in `./downloads`.

The app implements delta synchronization, meaning it will only fetch new messages that haven't been stored in the database yet.