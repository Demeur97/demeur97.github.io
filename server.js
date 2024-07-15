const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');

const app = express();
const port = 3000;

const connection = mysql.createConnection({
  host: 'server41.hosting.reg.ru',
  user: 'u2722842_eugpriv',
  password: 'eugprivEUGPRIV',
  database: 'u2722842_referal'
});

connection.connect(err => {
  if (err) {
    console.error('Error connecting to MySQL:', err);
    return;
  }
  console.log('Connected to MySQL');

  const createTableQuery = `
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255) NOT NULL,
      points INT DEFAULT 0,
      referral_code VARCHAR(255) UNIQUE
    )
  `;

  connection.query(createTableQuery, (err, result) => {
    if (err) {
      console.error('Error creating table:', err);
      return;
    }
    console.log('Table created or already exists');
  });
});

app.use(bodyParser.json());

app.post('/referral', (req, res) => {
  const { userId, referralId } = req.body;

  if (!userId || !referralId) {
    res.status(400).send('Invalid request');
    return;
  }

  const findUserQuery = 'SELECT * FROM users WHERE id = ?';
  connection.query(findUserQuery, [userId], (err, results) => {
    if (err) {
      console.error('Error finding user:', err);
      res.status(500).send('Server error');
      return;
    }

    if (results.length === 0) {
      const insertUserQuery = 'INSERT INTO users (id, username, points, referral_code) VALUES (?, ?, ?, ?)';
      connection.query(insertUserQuery, [userId, `user${userId}`, 0, referralId], (err, result) => {
        if (err) {
          console.error('Error inserting user:', err);
          res.status(500).send('Server error');
          return;
        }
        res.json({ points: 0 });
      });
    } else {
      const user = results[0];
      res.json({ points: user.points });
    }
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
