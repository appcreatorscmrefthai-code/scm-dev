-- ============================================================================
--  ตั้งค่าผู้ใช้จากหน้าเว็บ (users.html) : เฉพาะ admin
--  รันใน Supabase > SQL Editor ครั้งเดียว (รันซ้ำได้)  ต้องมีตาราง profiles และฟังก์ชัน is_admin() จาก supabase_setup.sql อยู่แล้ว
-- ============================================================================
create or replace function public.admin_require() returns void
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.is_admin() then raise exception 'ต้องเป็น Admin'; end if;
end $$;

-- รายชื่อผู้ใช้ทั้งหมด (รวมบัญชีที่ยังไม่มีสิทธิ์)
create or replace function public.admin_users()
returns json language plpgsql security definer set search_path = public, auth as $$
begin
  perform public.admin_require();
  return coalesce((
    select json_agg(json_build_object(
             'user_id', u.id, 'email', u.email, 'name', coalesce(p.name, ''),
             'role', coalesce(p.role, ''), 'active', coalesce(p.active, false),
             'last_sign_in_at', u.last_sign_in_at)
           order by (p.user_id is null), p.role, p.name, u.email)
    from auth.users u left join public.profiles p on p.user_id = u.id), '[]'::json);
end $$;

-- ตั้งชื่อ / สิทธิ์ (admin | edit | viewer) / เปิด-ปิดการใช้งาน   p_role = '' คือถอนสิทธิ์ (เข้าใช้ระบบไม่ได้)
create or replace function public.admin_save_user(p_user uuid, p_name text, p_role text, p_active boolean)
returns json language plpgsql security definer set search_path = public, auth as $$
declare v_email text;
begin
  perform public.admin_require();
  if coalesce(p_role, '') not in ('', 'admin', 'edit', 'viewer') then raise exception 'สิทธิ์ไม่ถูกต้อง'; end if;
  if p_user = auth.uid() and (coalesce(p_role, '') <> 'admin' or not coalesce(p_active, false)) then
    raise exception 'ลดสิทธิ์หรือปิดบัญชีของตัวเองไม่ได้';
  end if;
  if coalesce(p_role, '') = '' then
    delete from public.profiles where user_id = p_user;
  else
    select coalesce(email, '') into v_email from auth.users where id = p_user;
    insert into public.profiles (user_id, email, name, role, active)
    values (p_user, coalesce(v_email, ''), trim(coalesce(p_name, '')), p_role, coalesce(p_active, true))
    on conflict (user_id) do update
      set name = excluded.name, role = excluded.role, active = excluded.active;
  end if;
  return json_build_object('ok', true);
end $$;

-- สร้างผู้ใช้ใหม่  p_login = ชื่อสั้น (เติม @scmdelivery.local ให้) หรืออีเมล
create or replace function public.admin_create_user(p_login text, p_password text, p_name text, p_role text)
returns json language plpgsql security definer set search_path = public, auth, extensions as $$
declare
  v_email text := lower(trim(coalesce(p_login, '')));
  v_id uuid := gen_random_uuid();
  c text;
begin
  perform public.admin_require();
  if v_email = '' then raise exception 'กรุณาระบุชื่อผู้ใช้'; end if;
  if position('@' in v_email) = 0 then v_email := v_email || '@scmdelivery.local'; end if;
  if length(coalesce(p_password, '')) < 6 then raise exception 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'; end if;
  if p_role not in ('admin', 'edit', 'viewer') then raise exception 'สิทธิ์ไม่ถูกต้อง'; end if;
  if exists (select 1 from auth.users where lower(email) = v_email) then
    raise exception 'มีผู้ใช้ % อยู่แล้ว', v_email;
  end if;

  insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
                          raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
  values ('00000000-0000-0000-0000-000000000000', v_id, 'authenticated', 'authenticated', v_email,
          extensions.crypt(p_password, extensions.gen_salt('bf')), now(),
          '{"provider":"email","providers":["email"]}'::jsonb, jsonb_build_object('name', trim(coalesce(p_name, ''))),
          now(), now());
  -- ช่อง token ที่ระบบ login อ่านเป็นข้อความ ต้องไม่เป็น null
  foreach c in array array['confirmation_token', 'recovery_token', 'email_change_token_new', 'email_change',
                           'email_change_token_current', 'phone_change', 'phone_change_token', 'reauthentication_token']
  loop
    if exists (select 1 from information_schema.columns
               where table_schema = 'auth' and table_name = 'users' and column_name = c) then
      execute format('update auth.users set %I = '''' where id = $1 and %I is null', c, c) using v_id;
    end if;
  end loop;

  insert into auth.identities (id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
  values (gen_random_uuid(), v_id, v_id::text,
          jsonb_build_object('sub', v_id::text, 'email', v_email, 'email_verified', true),
          'email', now(), now(), now());

  -- trigger handle_new_user สร้างแถว profiles (viewer) ให้แล้ว : ทับด้วยสิทธิ์ที่เลือก
  insert into public.profiles (user_id, email, name, role, active)
  values (v_id, v_email, trim(coalesce(p_name, '')), p_role, true)
  on conflict (user_id) do update set name = excluded.name, role = excluded.role, active = true;
  return json_build_object('ok', true, 'user_id', v_id, 'email', v_email);
end $$;

-- ตั้งรหัสผ่านใหม่ให้ผู้ใช้
create or replace function public.admin_set_password(p_user uuid, p_password text)
returns json language plpgsql security definer set search_path = public, auth, extensions as $$
begin
  perform public.admin_require();
  if length(coalesce(p_password, '')) < 6 then raise exception 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร'; end if;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf')), updated_at = now()
   where id = p_user;
  return json_build_object('ok', true);
end $$;

revoke all on function public.admin_require()                                from public, anon;
revoke all on function public.admin_users()                                  from public, anon;
revoke all on function public.admin_save_user(uuid, text, text, boolean)     from public, anon;
revoke all on function public.admin_create_user(text, text, text, text)      from public, anon;
revoke all on function public.admin_set_password(uuid, text)                 from public, anon;
grant execute on function public.admin_require()                             to authenticated;
grant execute on function public.admin_users()                               to authenticated;
grant execute on function public.admin_save_user(uuid, text, text, boolean)  to authenticated;
grant execute on function public.admin_create_user(text, text, text, text)   to authenticated;
grant execute on function public.admin_set_password(uuid, text)              to authenticated;
