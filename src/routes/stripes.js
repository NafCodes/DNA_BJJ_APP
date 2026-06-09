import { Router } from 'express';
import { supabase } from '../lib/supabase.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

// GET /stripes — list stripes, optionally filter by student_id
router.get('/', requireAuth, async (req, res) => {
  const { student_id } = req.query;

  let query = supabase.from('stripes').select('*').order('stripe_number');

  if (student_id) query = query.eq('student_id', student_id);

  const { data, error } = await query;

  if (error) return res.status(500).json({ error: error.message });
  res.json(data);
});

// POST /stripes — award a stripe to a student
router.post('/', requireAuth, async (req, res) => {
  const { student_id, stripe_number, awarded_date } = req.body;

  if (!student_id || !stripe_number) {
    return res.status(400).json({ error: 'student_id and stripe_number are required' });
  }

  if (stripe_number < 1 || stripe_number > 4) {
    return res.status(400).json({ error: 'stripe_number must be between 1 and 4' });
  }

  const { data, error } = await supabase
    .from('stripes')
    .insert({ student_id, stripe_number, awarded_date })
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });
  res.status(201).json(data);
});

// DELETE /stripes/:id — revoke a stripe
router.delete('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;

  const { error } = await supabase
    .from('stripes')
    .delete()
    .eq('id', id);

  if (error) return res.status(500).json({ error: error.message });
  res.status(204).send();
});

export default router;
