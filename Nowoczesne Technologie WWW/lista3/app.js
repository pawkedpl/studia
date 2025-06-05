const express = require('express');
const app = express();
const dotenv = require('dotenv');
const connectDB = require('./config/db');
const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const reviewRoutes = require('./routes/reviews');
const userRoutes = require('./routes/users');
const errorHandler = require('./middlewares/errorHandler'); // jeœli masz

dotenv.config();

connectDB();

app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/products', productRoutes);
app.use('/api/reviews', reviewRoutes);
app.use('/api/users', userRoutes);

app.use(errorHandler); // jeœli masz ten middleware

module.exports = app;
