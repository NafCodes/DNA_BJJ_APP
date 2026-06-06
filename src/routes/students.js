import { Router } from 'express';
import { supabase } from '../lib/supabase.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

// GET /students — list all students
router.get('/', requireAuth, async (req, res) => {
  const { data, error } = await supabase
    .from('students')
    .select('*')
    .order('name');

  if (error) return res.status(500).json({ error: error.message });
  res.json(data);
});

// POST /students — add a new student
router.post('/', requireAuth, async (req, res) => {
  const { name, email, phone, belt_level, join_date } = req.body;

  if (!name || !email) {
    return res.status(400).json({ error: 'name and email are required' });
  }

  const { data, error } = await supabase
    .from('students')
    .insert({ name, email, phone, belt_level, join_date })
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });
  res.status(201).json(data);
});

// PATCH /students/:id — update a student
router.patch('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const updates = req.body;

  const { data, error } = await supabase
    .from('students')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });
  if (!data) return res.status(404).json({ error: 'Student not found' });
  res.json(data);
});

// DELETE /students/:id — remove a student
router.delete('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;

  const { error } = await supabase
    .from('students')
    .delete()
    .eq('id', id);

  if (error) return res.status(500).json({ error: error.message });
  res.status(204).send();
});

export default router;
