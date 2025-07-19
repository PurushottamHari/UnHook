# UnHook

## Setup

Follow these steps to set up the development environment for this project:

1. **Create and activate a Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Update local dependency paths in `pyproject.toml` files:**
   - Ensure that the local dependency paths in the `pyproject.toml` files for each service reflect your local directory structure. For example, update lines like:
     ```toml
     user-service @ file:///Users/puru/Workspace/UnHook/user_service
     data-collector-service @ file:///Users/puru/Workspace/UnHook/data_collector_service
     ```
     to match your actual local path if it differs.

3. **Install each service in editable mode:**
   - From the root of your project, run the following commands for each service:

   ```bash
   cd user_service
   python3 -m pip install -e .
   cd ../data_collector_service
   python3 -m pip install -e .
   cd ../data_processing_service
   python3 -m pip install -e .
   cd ..
   ```

4. **Create a `.env` file in each module:**
   - In each of the following directories: `user_service`, `data_collector_service`, and `data_processing_service`, create a `.env` file with the following content:
     ```env
     MONGODB_URI=your_mongodb_connection_string
     ```
   - Replace `your_mongodb_connection_string` with your actual MongoDB URI.

This will ensure all dependencies are installed and local packages are linked in editable mode for development.

## Code Formatting

This project uses **Black** and **isort** for automatic code formatting and import sorting. Configuration for both tools is included in each service's `pyproject.toml` file.

To format your code, run the following commands from the root of each service:

```bash
black . && isort .
```

This will ensure your code is consistently formatted and imports are properly organized.

## Running the Data Collector Service

To start the data collector service, run the following command from the root of your project:

```bash
python3 -m data_collector_service.service
```

# Moderation (Content Rejection) Step

To run the content moderation (rejection) step, use the following command from the project root:

```sh
python3 -m data_processing_service.services.rejection.reject_content_service
```

# Processing Moderated Content Step

To process the moderated content, use the following command from the project root:

```sh
python3 -m data_processing_service.services.processing.process_moderated_content_service
```


