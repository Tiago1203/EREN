const { createClient } = require('@supabase/supabase-js');

const url = 'https://mgzwhqejmifnmxplmwfn.supabase.co';
const key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1nendocWVqbWlmbm14cGxtd2ZuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjQwMTM2NiwiZXhwIjoyMDk3OTc3MzY2fQ.zSH7U5HIIeWo-xBdyL2q43HHe2QB5ZwF_tSwxInGE30';

const supabase = createClient(url, key, {
  auth: { persistSession: false }
});

const adminEmail = 'admin@biomedico.com';
const adminPassword = 'AdminBio2026!';
const clinicEmail = 'clinica.mcp@demo.com';
const clinicPassword = 'ClinicaMCP2026!';
const clinicRuc = '1790012345001';

async function main() {
  console.log('Starting user setup...');

  const { data: adminProfile, error: adminProfileError } = await supabase
    .from('profiles')
    .select('id,email,role,establecimiento_id')
    .eq('email', adminEmail)
    .single();

  if (adminProfileError && adminProfileError.code !== 'PGRST116') {
    console.error('Error loading admin profile:', adminProfileError);
    return;
  }

  if (!adminProfile) {
    console.log('Admin profile not found. Cannot update admin password without auth user id.');
  } else {
    console.log('Admin profile found:', adminProfile.id);
    const { data, error } = await supabase.auth.admin.updateUserById(adminProfile.id, {
      password: adminPassword,
      email: adminEmail,
      user_metadata: { name: 'Administrador BioMédico' }
    });
    if (error) {
      console.error('Admin updateUserById error:', error);
    } else {
      console.log('Admin password updated. User id:', data?.id);
    }
  }

  const { data: existingClinicProfile, error: existingClinicProfileError } = await supabase
    .from('profiles')
    .select('id,email,role,establecimiento_id')
    .eq('email', clinicEmail)
    .single();

  if (existingClinicProfileError && existingClinicProfileError.code !== 'PGRST116') {
    console.error('Error loading clinic profile:', existingClinicProfileError);
    return;
  }

  let clinicUserId = existingClinicProfile?.id;
  if (existingClinicProfile) {
    console.log('Clinic profile already exists:', clinicUserId);
  } else {
    console.log('Clinic profile not found. Creating auth user...');
    const { data: createUserData, error: createUserError } = await supabase.auth.admin.createUser({
      email: clinicEmail,
      password: clinicPassword,
      email_confirm: true,
      user_metadata: { name: 'Clínica MCP Demo' },
      app_metadata: { role: 'establecimiento' }
    });
    if (createUserError) {
      console.error('Error creating clinic auth user:', createUserError);
    } else {
      clinicUserId = createUserData.id;
      console.log('Clinic auth user created:', clinicUserId);
    }
  }

  if (!clinicUserId) {
    console.error('Clinic user id not available; aborting profile creation.');
    return;
  }

  const { data: establishment, error: establishmentError } = await supabase
    .from('establecimientos')
    .select('id')
    .eq('ruc', clinicRuc)
    .single();

  if (establishmentError) {
    console.error('Error finding clinic establishment:', establishmentError);
    return;
  }

  const establishmentId = establishment.id;
  console.log('Clinic establishment id:', establishmentId);

  if (!existingClinicProfile) {
    const { error: insertProfileError } = await supabase.from('profiles').insert({
      id: clinicUserId,
      email: clinicEmail,
      nombre: 'Clínica MCP Demo',
      role: 'establecimiento',
      establecimiento_id: establishmentId,
      is_active: true
    });
    if (insertProfileError) {
      console.error('Error inserting clinic profile:', insertProfileError);
    } else {
      console.log('Clinic profile inserted.');
    }
  }

  const { error: updateEstablishmentError } = await supabase
    .from('establecimientos')
    .update({ user_id: clinicUserId })
    .eq('ruc', clinicRuc);
  if (updateEstablishmentError) {
    console.error('Error updating establecimiento user_id:', updateEstablishmentError);
  } else {
    console.log('Clinic establishment user_id linked.');
  }

  console.log('Done. Use these credentials:');
  console.log(`- Admin: ${adminEmail} / ${adminPassword}`);
  console.log(`- Establecimiento: ${clinicEmail} / ${clinicPassword}`);
}

main().catch((err) => {
  console.error('Unexpected error', err);
  process.exit(1);
});
