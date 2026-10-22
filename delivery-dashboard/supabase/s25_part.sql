-- ============================================================================
--  รุ่น s25 : แสดง "อัปเดตแผนล่าสุดเมื่อ" = รอบที่บอตทำงานล่าสุด (แม้ข้อมูลไม่เปลี่ยน) หรือคนส่งจาก Excel ถ้าใหม่กว่า
--  รันใน Supabase > SQL Editor ครั้งเดียว (รันซ้ำได้) ต้องรัน s22 มาก่อน
-- ============================================================================
create or replace function public.bot_ping() returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_who text; v_now timestamptz := now();
begin
  if not public.is_member() then raise exception 'FORBIDDEN'; end if;
  select coalesce(nullif(name, ''), email) into v_who from public.profiles where user_id = auth.uid();
  insert into public.app_flags (key, value, at) values ('last_bot_run', coalesce(v_who, ''), v_now)
  on conflict (key) do update set value = excluded.value, at = excluded.at;
  return jsonb_build_object('at', v_now);
end $$;
revoke all on function public.bot_ping() from public, anon;
grant execute on function public.bot_ping() to authenticated;

create or replace function public.plan_last_sync() returns json
language plpgsql stable security definer set search_path = public as $$
declare a public.app_flags; b public.app_flags;
begin
  if not public.is_member() then raise exception 'FORBIDDEN'; end if;
  select * into a from public.app_flags where key = 'last_plan_sync';
  select * into b from public.app_flags where key = 'last_bot_run';
  if a.key is null and b.key is null then return json_build_object('at', null, 'by', ''); end if;
  if b.key is not null and (a.key is null or b.at >= a.at) then return json_build_object('at', b.at, 'by', b.value); end if;
  return json_build_object('at', a.at, 'by', a.value);
end $$;
revoke all on function public.plan_last_sync() from public, anon;
grant execute on function public.plan_last_sync() to authenticated;
