import { useState, useEffect } from 'react';

function Rating({ albumId, initialRating = 0, onRatingChange }) {
  const [rating, setRating] = useState(initialRating);
  const [hover, setHover] = useState(0);
  const [userRating, setUserRating] = useState(null);
  const [averageRating, setAverageRating] = useState(initialRating);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/auth/check/', {
          credentials: 'include'
        });
        setIsLoggedIn(response.ok);
      } catch (error) {
        setIsLoggedIn(false);
      }
    };
    checkAuth();
  }, []);

  // Fetch the user's rating and the average from the server
  useEffect(() => {
    const fetchRating = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/albums/${albumId}/rating/`, {
          credentials: 'include'
        });
        if (response.ok) {
          const data = await response.json();
          setUserRating(data.user_rating);
          setAverageRating(data.average_rating);
        }
      } catch (error) {
        console.error(error);
      }
    };
    fetchRating();
  }, [albumId]);

  const handleRate = async (value) => {
    if (!isLoggedIn) {
      alert('You must be logged in to rate');
      return;
    }

    setRating(value);

    try {
      const response = await fetch(`http://localhost:8000/api/albums/${albumId}/rate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',  // Important: send the cookie with the request
        body: JSON.stringify({ score: value })
      });

      if (response.ok) {
        const data = await response.json();
        setAverageRating(data.average_rating);
        setUserRating(value);
        if (onRatingChange) onRatingChange(value);
      } else {
        const errorData = await response.json();
        alert('Error submitting rating: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error(error);
      alert('Error connecting to the server');
    }
  };

  return (
    <div className="rating-container">
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${star <= (hover || (userRating || rating)) ? 'filled' : ''}`}
            onClick={() => handleRate(star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
          >
            ★
          </span>
        ))}
      </div>
      <div className="rating-info">
        <span className="average-rating">⭐ Average: {averageRating.toFixed(1)} / 5</span>
        {userRating && <span className="user-rating">🎯 Your rating: {userRating}</span>}
        {!isLoggedIn && (
          <span className="login-warning">Log in to rate</span>
        )}
      </div>
    </div>
  );
}

export default Rating;