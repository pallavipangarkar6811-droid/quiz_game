# 🎯 Quiz Master - Advanced Quiz Game

A modern, feature-rich quiz game application built with Flask and Python. Challenge yourself across multiple categories and difficulty levels while competing on the leaderboard!

## ✨ Features

### 📚 Multiple Categories
- **General Knowledge** 🌍
- **Python Programming** 🐍
- **Mathematics** 🔢
- **History** 📚
- **Science** 🔬

Each category includes carefully crafted questions tailored to different skill levels.

### ⚡ Difficulty Levels
- **Easy** 🟢 - Perfect for beginners
- **Medium** 🟡 - Standard challenge
- **Hard** 🔴 - For experts

### 🎮 Gameplay Features
- ⏱️ **Real-time Timer** - Track time spent on each quiz
- 📊 **Progress Bar** - Visual indication of quiz progress
- 🏆 **Leaderboard** - Compete with other players
- 📈 **Statistics** - Detailed performance analytics
- 🎯 **Category Stats** - Track performance by category
- ✅ **Instant Feedback** - Know results immediately after completing the quiz
- 📱 **Responsive Design** - Play on desktop, tablet, or mobile

### 🔥 UI/UX Enhancements
- Modern gradient design with smooth animations
- Intuitive navigation and user interface
- Beautiful progress indicators and score visualization
- Personalized performance messages
- Responsive layouts for all device sizes
- Smooth transitions and micro-interactions

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Flask
- SQLite3 (included with Python)

### Installation

1. Clone or download the project
```bash
cd quiz_project
```

2. Install Flask
```bash
pip install flask
```

3. Run the application
```bash
python app.py
```

4. Open your browser and navigate to
```
http://localhost:5000
```

## 📁 Project Structure

```
quiz_project/
├── app.py                    # Main Flask application
├── quiz.db                   # SQLite database (auto-created)
├── README.md                 # This file
├── RUN_GUIDE.md              # Running instructions
├── static/
│   └── css/
│       └── style.css         # Main stylesheet
└── templates/
    ├── index.html            # Home page
    ├── category.html         # Category & difficulty selection
    ├── quiz.html             # Quiz question page
    ├── result.html           # Results page
    ├── leaderboard.html      # Global leaderboard
    └── stats.html            # Category statistics
```

## 🎯 How to Play

1. **Enter Your Name**
   - Visit the home page and enter your player name

2. **Select Category**
   - Choose from 5 different quiz categories

3. **Choose Difficulty**
   - Select Easy, Medium, or Hard level

4. **Answer Questions**
   - Read each question carefully
   - Select your answer from the options
   - Press Enter or click Next to proceed
   - Watch the timer count your quiz time!

5. **View Results**
   - See your score and performance statistics
   - Check your accuracy percentage
   - View time taken
   - Get personalized feedback

6. **Check Leaderboard**
   - See how you rank against other players
   - View top 3 performers on the podium
   - See detailed statistics for each entry

## 💾 Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    score INTEGER NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT DEFAULT 'medium',
    total_questions INTEGER DEFAULT 3,
    time_taken INTEGER,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 🔧 API Endpoints

### Page Routes
- `GET /` - Home page
- `POST /` - Submit name and go to category selection
- `GET/POST /category` - Category and difficulty selection
- `GET/POST /quiz` - Quiz questions
- `GET /result` - Quiz results
- `GET /leaderboard` - View leaderboard

### API Endpoints
- `GET /api/get-time` - Get server timestamp for timer sync

## 🎨 Styling & Animations

The application features:
- **Gradient backgrounds** with smooth color transitions
- **Bounce animations** for medals and scores
- **Hover effects** on interactive elements
- **Smooth transitions** for all state changes
- **Responsive grid layouts** that adapt to all screen sizes
- **Custom progress indicators** with color-coded difficulty levels

### Color Scheme
- **Primary**: #667eea (Purple-Blue)
- **Secondary**: #764ba2 (Dark Purple)
- **Success**: #4ade80 (Green)
- **Warning**: #fbbf24 (Amber)
- **Danger**: #ef4444 (Red)

## 📊 Code Quality & Architecture

### Best Practices Implemented
- **Modular Functions** - Separated concerns (database, routes, utilities)
- **Error Handling** - Try-except blocks for database operations
- **Session Management** - Secure session handling with decorators
- **Database Optimization** - Connection pooling and efficient queries
- **Security** - Input validation and XSS protection
- **Code Comments** - Clear documentation of complex logic
- **Responsive Design** - Mobile-first approach with media queries

### Performance Optimizations
- Lightweight CSS without external dependencies
- Minimal JavaScript for fast loading
- Efficient database queries with proper indexing
- Session-based data storage to avoid repeated DB calls
- Client-side timer to reduce server load

## 🚀 Advanced Features

### Timer System
- Real-time countdown on quiz page
- Visual indicators for time elapsed
- Warning states after 2 minutes
- Danger state after 3 minutes
- Automatic time tracking for leaderboard

### Leaderboard Features
- Sorted by score (descending) and time (ascending)
- Top 3 performers highlighted on podium
- Detailed statistics per entry
- Category and difficulty tracking
- Date/time of quiz completion

### Statistics Tracking
- Per-category performance analytics
- Average score calculations
- Best score tracking
- Total plays counter
- Time-based comparisons

## 🎓 Educational Value

This project demonstrates:
- Flask web framework basics
- Database design and management
- Session handling in web applications
- RESTful API design principles
- Frontend-backend integration
- Responsive web design
- User experience considerations
- State management
- Error handling and validation

## 🔮 Future Enhancements

Potential improvements for the project:
- User authentication and accounts
- Social sharing of scores
- Achievement badges
- Hint system for questions
- Question explanations
- Timed countdown mode
- Multiplayer real-time quizzes
- Question difficulty ratings based on performance
- Advanced analytics dashboard
- Mobile app version
- Sound effects and background music
- Question submission from users
- Custom quiz creation
- Import questions from external APIs

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors, delete `quiz.db` and restart the app to reinitialize.

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
app.run(debug=True, host="0.0.0.0", port=5001)  # Use 5001 instead
```

### Session Issues
Clear browser cookies if session data appears corrupted.

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Contributing

Feel free to fork, modify, and improve this project!

## 🙏 Credits

Built as a comprehensive quiz game application with modern UI/UX principles.

---

**Ready to test your knowledge? Start playing now! 🎯**