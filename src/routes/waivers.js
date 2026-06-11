import { Router } from 'express';
import { supabase } from '../lib/supabase.js';

const router = Router();

// POST /waivers — public, no auth required (students sign via QR code)
router.post('/', async (req, res) => {
  const { name, email, signature, date_signed, expires } = req.body;

  if (!name || !email || !signature) {
    return res.status(400).json({ error: 'name, email, and signature are required' });
  }

  const { data, error } = await supabase
    .from('waivers')
    .insert({ name, email, signature, date_signed, expires })
    .select()
    .single();

  if (error) return res.status(500).json({ error: error.message });

  // Best-effort: mark matched student as waiver active
  await supabase
    .from('students')
    .update({ waiver_active: true })
    .eq('email', email);

  res.status(201).json(data);
});

export default router;
