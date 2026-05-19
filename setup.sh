#!/bin/bash
# Funda Malitinne LMS - Local Development Setup Script

set -e

echo "=================================================="
echo "Funda Malitinne LMS - Development Setup"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ Please edit .env with your settings"
else
    echo "✓ .env file already exists"
fi

# Create directories
mkdir -p media
mkdir -p staticfiles
mkdir -p logs
echo "✓ Directories created"

# Run migrations
echo "Running migrations..."
python manage.py migrate
echo "✓ Migrations completed"

# Create demo data
echo "Creating demo data..."
python manage.py create_demo_data
echo "✓ Demo data created"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

echo ""
echo "=================================================="
echo "✓ Setup Complete!"
echo "=================================================="
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate (if not already activated)"
echo "  python manage.py runserver"
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: admin123456"
echo ""
echo "Access the application at: http://localhost:8000"
echo ""
