const express = require('express');
const router = express.Router();
const Review = require('../models/Review');
const { protect } = require('../middlewares/auth');

router.post('/', protect, async (req, res) => {
    try {
        const review = await Review.create({ ...req.body, user: req.user.id });
        res.status(201).json(review);
    } catch (err) {
        res.status(400).json({ message: 'Error adding review' });
    }
});

router.get('/', async (req, res) => {
    try {
        const reviews = await Review.find().populate('product').populate('user', 'username');
        res.status(200).json(reviews);
    } catch (err) {
        res.status(500).json({ message: 'Error fetching reviews' });
    }
});

module.exports = router;
