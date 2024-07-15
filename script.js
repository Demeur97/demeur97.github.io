import { initUtils } from '@tma.js/sdk';
const utils = initUtils();

let tg = window.Telegram.WebApp;
tg.ready();
const user = tg.initDataUnsafe.user;

document.getElementById('userName').innerText = `${user.first_name} ${user.last_name}`;

document.getElementById('startButton').addEventListener('click', () => {
  const registrationDate = new Date(user.registration_date * 1000);
  const now = new Date();
  const timeElapsed = Math.floor((now - registrationDate) / (1000 * 60 * 60 * 24));
  document.getElementById('timeElapsed').innerText = `Прошло дней с момента регистрации: ${timeElapsed}`;
});

fetch('/referral', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ userId: user.id, referralId: 'some-referral-id' })
})
.then(response => response.json())
.then(data => {
  document.getElementById('referralCount').innerText = `Ваши рефералы: ${data.referralCount}`;
})
.catch(error => {
  console.error('Error:', error);
});

document.getElementById('referralButton').addEventListener('click', () => {
  const referralLink = `https://t.me/ProjectAprilBot/start?startapp=id${user.id}`;
  document.getElementById('referralLink').value = referralLink;
  document.getElementById('referralLink').select();
  document.execCommand('copy');
  alert('Referral link copied to clipboard!');
});

document.getElementById('shareButton').addEventListener('click', () => {
  const referralLink = document.getElementById('referralLink').value;
  tg.sendData(referralLink);
});

document.getElementById('navHome').addEventListener('click', () => {
  showPage('home');
});

document.getElementById('navTasks').addEventListener('click', () => {
  showPage('tasks');
});

document.getElementById('navFriends').addEventListener('click', () => {
  showPage('friends');
});

function showPage(pageId) {
  document.querySelectorAll('.page').forEach(page => {
    page.classList.remove('active');
  });
  document.getElementById(pageId).classList.add('active');

  document.querySelectorAll('.nav-button').forEach(button => {
    button.classList.remove('active');
  });
  document.getElementById(`nav${pageId.charAt(0).toUpperCase() + pageId.slice(1)}`).classList.add('active');
}

// Новый код для пересылки реферальной ссылки
const messageText = encodeURIComponent('🎉 Присоединяйтесь к нашему проекту и получайте бонусы!');
document.getElementById('forwardButton').addEventListener('click', () => {
  const referralLink = `https://t.me/ProjectAprilBot/start?startapp=id${user.id}`;
  utils.openTelegramLink(
    `https://t.me/share/url?url=${referralLink}&text=${messageText}`
  );
});
