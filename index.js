const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
app.use(bodyParser.json());

const PORT = process.env.PORT || 3000;

let users = {};

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

app.post('/referral', (req, res) => {
  const { userId, referralId } = req.body;

  if (!users[userId]) {
    users[userId] = { points: 0, referrals: [] };
  }

  if (referralId && !users[referralId]) {
    users[referralId] = { points: 0, referrals: [] };
  }

  if (referralId && !users[userId].referrals.includes(referralId)) {
    users[userId].referrals.push(referralId);
    users[userId].points += 10; // Начисляем 10 баллов за каждого реферала
  }

  res.send({ points: users[userId].points });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
