# Make the main script executable
chmod +x main.py

# Create necessary directories
mkdir -p logs data tests

# Initialize git repository
git init
git add .
git commit -m "Initial commit: Company Data Collection Prototype"

echo "Setup complete! Next steps:"
echo "1. Copy config.env.example to .env and configure your settings"
echo "2. Set up PostgreSQL database"
echo "3. Run: python main.py --init-db"
echo "4. Run: python main.py"
