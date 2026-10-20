-- ============================================================================
--  รุ่น s22 : บันทึกเวลาส่งแผนขึ้นระบบล่าสุด (แสดงที่ Dashboard) + เพดานรูป WH ในประเทศ 50 รูป
--  รันใน Supabase > SQL Editor ครั้งเดียว (รันซ้ำได้) ต้องมีตาราง app_flags อยู่แล้ว
-- ============================================================================
create table if not exists public.app_flags (key text primary key, value text not null default '', at timestamptz not null default now());

create or replace function public.plan_sync(p_rows jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare r jsonb; v_code text; v_date date; v_who text; v_ins int := 0; v_upd int := 0; v_now timestamptz := now(); v_new boolean;
begin
  if not public.can_edit() then raise exception 'FORBIDDEN'; end if;
  select coalesce(nullif(name, ''), email) into v_who from public.profiles where user_id = auth.uid();
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception 'ไม่มีข้อมูล'; end if;
  for r in select * from jsonb_array_elements(p_rows) loop
    v_code := btrim(coalesce(r->>'task_code', ''));
    if v_code = '' then continue; end if;
    v_date := public.to_date_loose(r->>'date');
    if v_date is null then raise exception 'งาน %: วันที่ไม่ถูกต้อง (%)', v_code, coalesce(r->>'date', ''); end if;
    insert into public.plan as t (task_code, date, detail, client, job_type, transport, schedule, arr1, arr2, arr3, company, vehicle_type, plate, driver, phone, round,
        stop1, map1, rec1, stop2, map2, rec2, stop3, map3, rec3, status, updated_at, updated_by)
    values (v_code, v_date, public.blank(r->>'detail'), public.blank(r->>'client'), lower(public.blank(r->>'job_type')), public.blank(r->>'transport'),
        public.hm(r->>'schedule'), public.hm(r->>'arr1'), public.hm(r->>'arr2'), public.hm(r->>'arr3'),
        public.blank(r->>'company'), public.blank(r->>'vehicle_type'), public.blank(r->>'plate'), public.blank(r->>'driver'), public.blank(r->>'phone'), public.blank(r->>'round'),
        public.blank(r->>'stop1'), public.blank(r->>'map1'), public.blank(r->>'rec1'), public.blank(r->>'stop2'), public.blank(r->>'map2'), public.blank(r->>'rec2'),
        public.blank(r->>'stop3'), public.blank(r->>'map3'), public.blank(r->>'rec3'), public.blank(r->>'status'), v_now, v_who)
    on conflict (task_code) do update set
        date = excluded.date, detail = excluded.detail, client = excluded.client, transport = excluded.transport, schedule = excluded.schedule,
        job_type = case when r ? 'job_type' then excluded.job_type else t.job_type end,
        arr1 = excluded.arr1, arr2 = excluded.arr2, arr3 = excluded.arr3, company = excluded.company, vehicle_type = excluded.vehicle_type,
        plate = excluded.plate, driver = excluded.driver, phone = excluded.phone, round = excluded.round,
        stop1 = excluded.stop1, map1 = excluded.map1, rec1 = excluded.rec1, stop2 = excluded.stop2, map2 = excluded.map2, rec2 = excluded.rec2,
        stop3 = excluded.stop3, map3 = excluded.map3, rec3 = excluded.rec3, status = excluded.status, updated_at = excluded.updated_at, updated_by = excluded.updated_by
    returning (t.created_at = v_now) into v_new;
    if v_new then v_ins := v_ins + 1; else v_upd := v_upd + 1; end if;
  end loop;
  if v_ins + v_upd > 0 then      -- s22 : จำไว้ว่าส่งแผนขึ้นระบบล่าสุดเมื่อไหร่ ใคร (Bot / คน) ใช้แสดงที่ Dashboard
    insert into public.app_flags (key, value, at) values ('last_plan_sync', coalesce(v_who, ''), v_now)
    on conflict (key) do update set value = excluded.value, at = excluded.at;
  end if;
  return jsonb_build_object('inserted', v_ins, 'updated', v_upd);
end $$;

-- s22 : ส่งแผนขึ้นระบบล่าสุดเมื่อไหร่ (ดูที่ Dashboard) : { at, by }
create or replace function public.plan_last_sync() returns json
language plpgsql stable security definer set search_path = public as $$
declare r public.app_flags;
begin
  if not public.is_member() then raise exception 'FORBIDDEN'; end if;
  select * into r from public.app_flags where key = 'last_plan_sync';
  if not found then return json_build_object('at', null, 'by', ''); end if;
  return json_build_object('at', r.at, 'by', r.value);
end $$;
revoke all on function public.plan_last_sync() from public, anon;
grant execute on function public.plan_last_sync() to authenticated;

create or replace function public.dept_photo_max(p_dept text, p_intl boolean default false) returns int
language sql immutable as $$ select case when p_intl then 300 when p_dept = 'QA' then 50 else 50 end $$;
