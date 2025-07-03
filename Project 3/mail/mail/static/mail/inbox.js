
document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('#compose-view').style.display = 'none';

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  //Send mail
  document.querySelector('#compose-form').onsubmit = function(event) {
    event.preventDefault(); // Frenar el envio tradicional

    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    fetch('/emails', {
      method : 'POST',
      body : JSON.stringify({
        recipients : recipients,
        subject : subject,
        body : body
      }),
      headers: {
        'Content-Type' : 'application/json'
      }
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      load_mailbox('sent');
    })
    

  }
});



function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  //Fetch to backend
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      const template = document.getElementById('email-template');
      const container = document.getElementById('emails-view');

      emails.forEach(email => {
        const clone = template.content.cloneNode(true);

        if (mailbox === 'sent'){
          clone.querySelector('.email-name').innerText = email.recipients.join(', ');
          clone.querySelector('.archive').style.display = 'none';

        } else {
          clone.querySelector('.email-name').innerText = email.sender;
          clone.querySelector('.archive').style.display = 'inline';
        }
        clone.querySelector('.email-subject').innerText = email.subject;
        clone.querySelector('.email-time').innerText = email.timestamp;
        if (email.read == false) {
             clone.querySelector('.email-item').classList.add('email-unread');
        }
        if (email.archived) {
            clone.querySelector('.archive').src = 'https://cdn-icons-png.flaticon.com/512/6929/6929626.png';
        } else {
            clone.querySelector('.archive').src = 'https://static-00.iconduck.com/assets.00/archive-icon-2048x2048-k6f5jd4d.png';
        }

        clone.querySelector('.archive').addEventListener('click', (event) => {
          event.stopPropagation(); // Para que no se dispare view_email()
          const emailItem = event.target.closest('.email-item');
          emailItem.classList.add('fade-out');

          setTimeout ( ()=> {
            emailItem.remove();
            
            fetch(`/emails/${email.id}`, {
              method: 'PUT',
              body: JSON.stringify({ archived: !email.archived })
            })
            .then(() => load_mailbox('inbox'));
            }, 500);
        
        });

        clone.querySelector('.email-item').addEventListener('click', () => view_email(email.id));

        container.appendChild(clone);
        
      });
    })
}

function view_email(email_id){
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      document.querySelector('.email-subject').innerText = email.subject;
      document.querySelector('.email-sender').innerText = `From: ${email.sender}`;
      document.querySelector('.email-recipients').innerText = `To: ${email.recipients.join(', ')}`;
      document.querySelector('.email-body').innerText = email.body;

    const replyBtn = document.querySelector('#email-reply');
    replyBtn.onclick = () => reply_mail(email);

    if (email.read == false){
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            read: true
          })
        })
    }
    })
}

function reply_mail(email){
  compose_email();
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ') ? email.subject : `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `\n\n --------- On ${email.timestamp}, ${email.sender} wrote: --------- \n${email.body}`

}
