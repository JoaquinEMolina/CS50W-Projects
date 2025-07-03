document.addEventListener('DOMContentLoaded', function () {
    const username = USERNAME;
    document.querySelector('#profile-view').style.display = 'none';

    // Load All by default
    load_posts('all');

    // Delegación para ir a perfil al hacer click en un usuario
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('post-user')) {
            const user = event.target.textContent.trim();
            load_posts(user);
        }
    });

    // Navegación
    document.querySelectorAll('.btn-nav').forEach(btn => {
        btn.onclick = () => {
            const view = btn.dataset.view;
            load_posts(view);
        };
    });

    // Publicar post
    document.querySelector('#compose-form').onsubmit = function (event) {
        event.preventDefault();
        const body = document.querySelector('#compose-body').value.trim();

        if (!body) {
            alert("The content of the post is empty.");
            return;
        }

        fetch('create_post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ body })
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                alert(result.error);
            } else {
                document.querySelector('#compose-body').value = '';
                load_posts('all');
            }
        })
        .catch(error => console.error('Error al enviar post:', error));
    };

    //Follow-Unfollow
    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("btn-follow") || event.target.classList.contains("btn-unfollow")) {
            const username = document.querySelector(".profile-user").textContent;

            fetch(`/follow_unfollow/${username}`, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector(".followers-count").textContent = data.followers_count;
                document.querySelector(".following-count").textContent = data.following_count;

                document.querySelector(".btn-follow").style.display = data.action === "followed" ? "none" : "inline-block";
                document.querySelector(".btn-unfollow").style.display = data.action === "followed" ? "inline-block" : "none";
            });
        }
    });

    //Like-Unlike
    document.addEventListener("click", function (event) {
        const btn = event.target.closest(".btn-like");
        if (btn) {
            const postCard = btn.closest(".card");
            const postId = postCard.dataset.id;
            const likeCountSpan = btn.querySelector(".like-count");
            

            fetch(`/like_unlike/${postId}`, {
                method: 'POST',
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            })
            .then(response => response.json())
            .then(data => {
                // Update likes count
                likeCountSpan.textContent = data.likes_count;
                // Change class
                btn.classList.toggle('btn-danger', data.liked);
                btn.classList.toggle('text-white', data.liked);
                btn.classList.toggle('btn-outline-danger', !data.liked);
            })
            .catch(error => console.error('Error like/unlike:', error));
        }
    });
});


function load_posts(view, page = 1) {
    const container = document.querySelector('#posts-view');
    container.classList.add('fade-out');

    container.addEventListener('transitionend', function handler() {
        container.removeEventListener('transitionend', handler);

        let endpoint = `/posts/${view}?page=${page}`;
        document.querySelector('#page-view').innerHTML = `<h3>${view.charAt(0).toUpperCase() + view.slice(1)}</h3>`;
        if (!USERNAME) {
            document.querySelector('h3').textContent = 'Login or register to view all posts!';
        }

        if (view === 'all' || view === 'following') {
            document.querySelector('#compose-post').style.display = 'block';
            document.querySelector('#profile-view').style.display = 'none';
        } else if (view === USERNAME) {
            document.querySelector('#compose-post').style.display = 'block';
            document.querySelector('#profile-view').style.display = 'block';
            document.querySelector('.btn-follow').style.display = 'none';
            document.querySelector('.btn-unfollow').style.display = 'none';
            fetch(`/profile/${USERNAME}`)
                .then(response => response.json())
                .then(profile => {
                    document.querySelector('.profile-user').textContent = profile.username;
                    document.querySelector('.followers-count').textContent = profile.followers;
                    document.querySelector('.following-count').textContent = profile.following;
                })
            .catch(error => console.error('Error cargando el perfil:', error));
        } else {
            document.querySelector('#compose-post').style.display = 'none';
            document.querySelector('#profile-view').style.display = 'block';

            fetch(`/profile/${view}`)
                .then(response => response.json())
                .then(profile => {
                    document.querySelector('.profile-user').textContent = profile.username;
                    document.querySelector('.followers-count').textContent = profile.followers;
                    document.querySelector('.following-count').textContent = profile.following;

                    const followBtn = document.querySelector('.btn-follow');
                    const unfollowBtn = document.querySelector('.btn-unfollow');

                    if (profile.username === USERNAME) {
                        followBtn.style.display = 'none';
                        unfollowBtn.style.display = 'none';
                    } else {
                        followBtn.style.display = profile.is_following ? 'none' : 'inline-block';
                        unfollowBtn.style.display = profile.is_following ? 'inline-block' : 'none';
                    }
                })
                .catch(error => console.error('Error cargando el perfil:', error));
        }

        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';
                data.posts.forEach(post => {
                    const postDiv = create_post_element(post);
                    container.appendChild(postDiv);
                });
                render_pagination(data, view);

                container.classList.remove('fade-out');
                container.classList.add('fade-in');
                container.addEventListener('animationend', function animHandler() {
                    container.classList.remove('fade-in');
                    container.removeEventListener('animationend', animHandler);
                });
            })
            .catch(error => console.error('Error cargando posts:', error));
    });
}


function create_post_element(post) {
    const template = document.querySelector('#post-template');
    const postElement = template.content.cloneNode(true);
    const card = postElement.querySelector('.card');
    card.dataset.id = post.id;

    postElement.querySelector('.post-user').textContent = post.user;
    postElement.querySelector('.post-content').textContent = post.body;
    postElement.querySelector('.post-date').textContent = post.timestamp;

    const editButton = postElement.querySelector('.btn-edit');
    if (post.user !== USERNAME) {
        editButton.style.display = 'none';
    } else {
        editButton.onclick = () => edit_post(post);
    }

    const likeButton = postElement.querySelector('.btn-like');
    const likeCount = likeButton.querySelector('.like-count');

    const likes = post.likes || { count: 0, liked: false };
    likeCount.textContent = likes.count;

    likeButton.classList.remove("btn-danger", "btn-outline-danger", "text-white");

    if (likes.liked) {
        likeButton.classList.add("btn-danger", "text-white");
    } else {
        likeButton.classList.add("btn-outline-danger");
    }

    return postElement;
}


function render_pagination(data, view) {
    const pagination = document.querySelector('.pagination');
    pagination.innerHTML = '';

    const prev = document.createElement('li');
    prev.className = `page-item ${!data.has_previous ? 'disabled' : ''}`;
    prev.innerHTML = `<a class="page-link" href="#">Previous</a>`;
    if (data.has_previous) {
        prev.onclick = () => load_posts(view, data.previous_page_number);
    }
    pagination.appendChild(prev);

    for (let i = 1; i <= data.num_pages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${i === data.current_page ? 'active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        pageItem.onclick = () => load_posts(view, i);
        pagination.appendChild(pageItem);
    }

    const next = document.createElement('li');
    next.className = `page-item ${!data.has_next ? 'disabled' : ''}`;
    next.innerHTML = `<a class="page-link" href="#">Next</a>`;
    if (data.has_next) {
        next.onclick = () => load_posts(view, data.next_page_number);
    }
    pagination.appendChild(next);
}


function edit_post(post) {
    const postCard = document.querySelector(`.card[data-id="${post.id}"]`);
    if (!postCard) return;

    const form = document.createElement('form');
    form.classList.add('mb-3');

    const textarea = document.createElement('textarea');
    textarea.classList.add('form-control');
    textarea.value = post.body;

    const saveButton = document.createElement('button');
    saveButton.className = 'btn btn-sm btn-primary mt-2 ms-3 btn-send';
    saveButton.textContent = 'Update';

    form.appendChild(textarea);
    form.appendChild(saveButton);

    const originalHTML = postCard.innerHTML;
    postCard.innerHTML = '';
    postCard.appendChild(form);

    form.onsubmit = function (event) {
        event.preventDefault();
        const newBody = textarea.value.trim();
        if (!newBody) {
            alert("The content cannot be empty.");
            return;
        }

        fetch(`/posts/${post.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ body: newBody })
        })
        .then(response => {
            if (!response.ok) throw new Error("Error updating post.");
            return response.json();
        })
        .then(updatedPost => {
            postCard.classList.add('fade-out');
            postCard.addEventListener('transitionend', function handler() {
                postCard.removeEventListener('transitionend', handler);
                const newPostElement = create_post_element(updatedPost);
                const newCard = newPostElement.querySelector('.card');
                postCard.replaceWith(newCard);
                newCard.classList.add('fade-in');
            });
        })
        .catch(error => {
            console.error("Error updating post:", error);
            postCard.innerHTML = originalHTML;
        });
    };
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
