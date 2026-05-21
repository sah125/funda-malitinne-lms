# Lesson Discussion Forum - Implementation Guide

## Overview
A complete threaded discussion forum system for lesson-level interactions in your Funda Malitinne LMS. Students, instructors, and admins can collaboratively discuss lesson content with nested replies and community engagement features.

## Features Implemented

### 1. **Database Models**
- **LessonDiscussion**: Main discussion post for a lesson
  - Title, content, author, creation date
  - Pinning for important discussions
  - Closing discussions to prevent new replies
  - View counter for engagement tracking
  
- **DiscussionReply**: Threaded replies with nesting support
  - Parent reply reference for nested conversations
  - Like counter for community engagement
  - Edit tracking (is_edited flag)
  - Automatic depth calculation for display
  
- **DiscussionLike**: User engagement tracking
  - One-to-one relationship (users can like replies once)
  - Automatic like count updates

### 2. **Views & URLs**
| Endpoint | URL | Purpose |
|----------|-----|---------|
| lesson_discussions | /lesson/<id>/discussions/ | List all discussions for a lesson |
| discussion_detail | /discussion/<id>/ | View single discussion with replies |
| delete_discussion | /api/discussion/<id>/delete/ | Delete discussion (author/instructor only) |
| delete_reply | /api/reply/<id>/delete/ | Delete reply (author/instructor only) |
| toggle_discussion_close | /api/discussion/<id>/toggle-close/ | Close/open discussion (instructor only) |
| like_reply | /api/reply/<id>/like/ | Like/unlike a reply (authenticated users) |

### 3. **Frontend Templates**
- **lesson_discussions.html**: Discussion listing page
  - Create new discussion form (collapsible)
  - Discussion cards with metadata (author, date, stats)
  - Reply and view counters
  - Pinned/Closed badges
  - Empty state messaging
  
- **discussion_detail.html**: Single discussion view
  - Full discussion content
  - Threaded reply system
  - Like buttons on replies
  - Reply forms with parent reply tracking
  - Edit/delete controls for owners/instructors

### 4. **Permissions & Access Control**
- Students/Instructors: Can view all lesson discussions
- All authenticated users: Can create discussions and reply
- Authors: Can delete their own discussions and replies
- Instructors: Can close discussions, delete any reply/discussion, pin discussions
- Admins: Can access and manage via Django admin panel

### 5. **Discussion Threading**
- Direct replies to main discussion
- Nested replies to specific comments (up to N levels)
- Visual indentation for reply hierarchy
- Automatic "replied to" indicators for nested replies

## Database Schema

```sql
-- Main discussion posts
CREATE TABLE core_lessondiscussion (
    id INTEGER PRIMARY KEY,
    lesson_id INTEGER REFERENCES core_lesson(id),
    author_id INTEGER REFERENCES auth_user(id),
    title VARCHAR(300),
    content TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    views_count INTEGER DEFAULT 0
);

-- Replies (threaded)
CREATE TABLE core_discussionreply (
    id INTEGER PRIMARY KEY,
    discussion_id INTEGER REFERENCES core_lessondiscussion(id),
    author_id INTEGER REFERENCES auth_user(id),
    parent_reply_id INTEGER REFERENCES core_discussionreply(id) NULL,
    content TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    is_edited BOOLEAN DEFAULT FALSE,
    likes_count INTEGER DEFAULT 0
);

-- User likes on replies
CREATE TABLE core_discussionlike (
    id INTEGER PRIMARY KEY,
    reply_id INTEGER REFERENCES core_discussionreply(id),
    user_id INTEGER REFERENCES auth_user(id),
    created_at DATETIME,
    UNIQUE(reply_id, user_id)
);
```

## User Workflows

### Creating a Discussion
1. Student/Instructor goes to lesson page
2. Clicks "Discussions" step in navigation
3. Clicks "Start New Discussion"
4. Enters title and description
5. Posts discussion
6. Discussion appears in list

### Replying to a Discussion
1. User opens a discussion from the list
2. Scrolls to reply form at bottom
3. Enters reply content
4. Posts reply
5. Reply appears in threaded view

### Nested Replies (Replying to Replies)
1. User hovers over a reply
2. Clicks "Reply" button
3. Nested reply form appears
4. Enters reply content
5. Reply appears nested under parent

### Engagement
1. Users can like replies (click thumbs up)
2. Like counters update in real-time
3. Instructors can pin important discussions
4. Instructors can close discussions
5. Deleted discussions removed from list

## Files Modified/Created

### New Files
- `templates/discussion/lesson_discussions.html` - Discussion listing page
- `templates/discussion/discussion_detail.html` - Single discussion view

### Modified Files
- `core/models.py` - Added 3 new models (LessonDiscussion, DiscussionReply, DiscussionLike)
- `core/views.py` - Added 7 new views for discussion management
- `core/admin.py` - Added 3 admin classes for model management
- `lms/urls.py` - Added 6 new URL patterns
- `templates/lesson_detail.html` - Added "Discussions" link to lesson navigation

### Generated Files
- `core/migrations/0006_lessondiscussion_discussionreply_discussionlike.py` - Database migration

## Installation & Setup

### 1. Apply Migrations
```bash
python manage.py makemigrations core
python manage.py migrate core
```

### 2. Access Points
- **Student/Instructor**: Visit any lesson page → Click "Discussions" step
- **Admin**: Django admin panel at `/admin/core/lessondiscussion/`

### 3. Testing
```bash
# Create test discussion
curl -X POST /lesson/1/discussions/ \
  -H "Content-Type: form-urlencoded" \
  -d "create_discussion=yes&title=Test&content=Test content"

# View discussions
curl /lesson/1/discussions/

# View single discussion
curl /discussion/1/
```

## Future Enhancements
- Markdown support for rich text discussions
- Discussion search functionality
- Email notifications for replies
- Discussion moderation queue
- Mention (@user) functionality
- Reaction emojis instead of just likes
- Discussion statistics and analytics
- Export discussions to PDF
- Spam detection and filtering

## Performance Considerations
- Discussion replies are ordered by creation time (ascending)
- Top-level replies prefetched with nested_replies
- Pagination can be added for discussions with many replies
- View counts updated sparingly (not on every load)

## Security
- CSRF protection on all forms
- Permission checks on all deletion endpoints
- User ownership verification before edit/delete
- HTML escaping on all user content
- Input validation on text fields

## Admin Panel Features
- Filter discussions by course and status
- Search by title or content
- Bulk actions (future implementation)
- View read-only fields (created_at, updated_at, views_count)
- Direct access to associated lessons and authors

---
**Version**: 1.0  
**Created**: 2026-05-21  
**Last Updated**: 2026-05-21
