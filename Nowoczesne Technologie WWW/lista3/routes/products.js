const express = require('express');
const router = express.Router();
const Product = require('../models/Product');
const { protect, authorize } = require('../middlewares/auth');

router.get('/', async (req, res) => {
    const { page = 1, limit = 10, sort = 'createdAt', category } = req.query;
    const query = category ? { category } : {};

    try {
        const products = await Product.find(query)
            .sort(sort)
            .skip((page - 1) * limit)
            .limit(Number(limit));

        const total = await Product.countDocuments(query);

        res.status(200).json({ total, page: Number(page), products });
    } catch (err) {
        res.status(500).json({ message: 'Error fetching products' });
    }
});

router.post('/', protect, authorize('admin'), async (req, res) => {
    try {
        const product = await Product.create(req.body);
        res.status(201).json(product);
    } catch (err) {
        res.status(400).json({ message: 'Error creating product' });
    }
});

router.put('/:id', protect, authorize('admin'), async (req, res) => {
    try {
        const updated = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true });
        res.status(200).json(updated);
    } catch (err) {
        res.status(400).json({ message: 'Error updating product' });
    }
});

router.delete('/:id', protect, authorize('admin'), async (req, res) => {
    try {
        await Product.findByIdAndDelete(req.params.id);
        res.status(204).end();
    } catch (err) {
        res.status(500).json({ message: 'Error deleting product' });
    }
});

module.exports = router;
