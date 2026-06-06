import { Router } from 'express';
import { supabase } from '../lib/supabase.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

// GET /attendance — list records, optionally filter by student_id or date
router.get('/', requireAuth, async (req, res) => {
  const { student_id, date } = req.query;

  let query = supabase.from('attendance').select('*').order('session_date', { ascending: false });

  if (student_id) query = query.eq('student_id', student_id);
  if (date)       query = query.eq('session_date', date);

  const { data, error } = await query;

  if (error) return res.status(500).json({ error: error.message });
  res.json(data);
});

// POST /attendance — check in a student
router.post('/', requireAuth, async (req, res) => {
  const { student_id, session_date } = req.body;

  if (!student_id) {
    return res.status(400).json({ error: 'student_id is required' });
  }

  const { data, error } = await supabase
    .from('attendance')
    .insert({ student_id, session_date })
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });
  res.status(201).json(data);
});

// DELETE /attendance/:id — remove an attendance record
router.delete('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;

  const { error } = await supabase
    .from('attendance')
    .delete()
    .eq('id', id);

  if (error) return res.status(500).json({ error: error.message });
  res.status(204).send();
});

export default router;
