import { useState, useEffect } from 'react';

function Comments({ albumId }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/auth/check/', {
          credentials: 'include'  // Important: send the cookie with the request
        });
        setIsLoggedIn(response.ok);
      } catch (error) {
        setIsLoggedIn(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    fetchComments();
  }, [albumId]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/albums/${albumId}/comments/`, {
        credentials: 'include'  // Important: send the cookie with the request
      });
      if (response.ok) {
        const data = await response.json();
        setComments(data);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const submitComment = async () => {
    if (!newComment.trim()) return;

    if (!isLoggedIn) {
      alert('You must be logged in to comment');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/albums/${albumId}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',  // Important: send the cookie with the request
        body: JSON.stringify({ body: newComment })
      });

      if (response.ok) {
        setNewComment('');
        fetchComments();
        alert('Your comment was submitted successfully!');
      } else {
        const errorData = await response.json();
        console.error(errorData);
        alert('Error submitting comment: ' + (errorData.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error(error);
      alert('Error connecting to the server');
    }
  };

  if (loading) return <div className="comments-loading">Loading comments...</div>;

  return (
    <div className="comments-section">
      <h3>💬 User Comments ({comments.length})</h3>

      <div className="comment-list">
        {comments.length === 0 ? (
          <p className="no-comments">No comments yet. Be the first!</p>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="comment-item">
              <div className="comment-header">
                <strong>{comment.user_name || 'User'}</strong>
                <small>{new Date(comment.created_at).toLocaleDateString('en-US')}</small>
              </div>
              <p className="comment-body">{comment.body}</p>
            </div>
          ))
        )}
      </div>

      {isLoggedIn ? (
        <div className="add-comment">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Write your comment..."
            rows="3"
          />
          <button onClick={submitComment} className="submit-comment-btn">
            Post Comment
          </button>
        </div>
      ) : (
        <p className="login-to-comment">
         <button onClick={() => window.location.href = '/login'}>Log in</button> to write a comment
        </p>
      )}
    </div>
  );
}

export default Comments;