FROM python:3.13

# Set working directory
WORKDIR /code

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy the entire project
COPY . .

# Install dependencies (runtime only)
RUN poetry install --without test

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "stargazer.main:app", "--host", "0.0.0.0",  "--port", "8000"]
