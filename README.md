# Hermius

##### *Currently a WIP. Expect bugs and errors to be present.*
Hermius is a secure and anonymous chatroom service that allows users to communicate without revealing their identity. Users can choose to chat anonymously or create an account for additional features. All messages are end-to-end encrypted, ensuring that only encrypted messages are stored in the database.

---

## Features

- **Anonymous Chat**: Join chatrooms without creating an account.
- **Account Management**: Create an account for additional features like modifying account details and accessing your user profile.
- **End-to-End Encryption**: Messages are encrypted using the `cryptography.fernet` library for secure storage.
- **Real-time Communication**: Powered by Flask and Socket.IO for seamless real-time messaging.
- **User Profiles**: View and modify user profiles, including username, email, and password.
- **Room Management**: Create and join chatrooms with unique codes.
- **Inactivity Cleanup**: Chatrooms are automatically deleted after a period of inactivity to keep the platform clean and efficient.
- **Emoji Support**: Use emojis in your messages with an integrated emoji picker.

---

## Technologies Used

- **Backend**: Flask, SQLite
- **Frontend**: HTML, CSS (TailwindCSS), JavaScript
- **Real-time Communication**: Socket.IO
- **Encryption**: Caesar cipher (future plans for AES-256 and RSA)

---

## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/TheRevanite/Hermius.git
    cd Hermius
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up the Database**:
    The database will be automatically set up when you run the application for the first time.

4. **Run the Application**:
    ```bash
    python main.py
    ```

5. **Access the Application**:
    Open your web browser and navigate to `http://localhost:5000`.

---

## File Structure

- **`main.py`**: Main application file that initializes the app and starts the server.
- **`app/`**: Contains the core application logic.
  - **`routes/`**: Contains route definitions for main, authentication, utility, and message-related functionality.
  - **`sockets/`**: Handles real-time Socket.IO events for messaging and room management.
  - **`state.py`**: Manages shared application state, including active rooms and users.
  - **`utils/`**: Utility functions for encryption and room code generation.
  - **`database/`**: Database connection and schema setup.
  - **`templates/`**: HTML templates for the frontend.
  - **`extensions.py`**: Initializes Flask extensions like Socket.IO and Flask-Mail.
- **`requirements.txt`**: Lists all dependencies required to run the project.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.

---

## Encryption Details

Hermius uses the `cryptography.fernet` library for encrypting messages. This ensures that messages are securely encrypted before being stored in the database and can only be decrypted using the generated key. Below is an overview of the encryption process:

- **Key Generation**: A unique key is generated using `Fernet.generate_key()`.
- **Message Encryption**: Messages are encrypted using the `Fernet` cipher suite.
- **Message Decryption**: Encrypted messages are decrypted using the same key.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. If you encounter any bugs or have feature requests, feel free to open an issue.

---

## Future Plans

- **Mobile App**: Develop a mobile app for Android and iOS.
- **Advanced Room Features**: Add support for private rooms, room moderators, and more.
- **Improved UI/UX**: Enhance the user interface for a more seamless experience.