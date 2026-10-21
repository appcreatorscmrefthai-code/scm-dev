-- ============================================================================
--  s23 (รันครั้งเดียวใน Supabase > SQL Editor ; รันซ้ำได้)
--   1) อายุ QR ทุกอัน (คนขับ / WH / QA / WH ต่างประเทศ) = เปิดได้ก่อนวันงาน 1 วัน ถึง วันงาน + 4 วัน
--   2) Admin เปิดฟอร์ม / อัปรูป / บันทึกข้อมูลได้ทุกช่วงเวลา (ไม่จำกัดวันที่และ 24 ชม.) ใช้ปุ่ม "อัปโหลดรูป + แก้ไขข้อมูล" ใน Popup ของ Dashboard
--   3) การแก้ไขงานเดิมจาก Excel / บอต (plan_update) ถูกนับเป็น "ส่งแผนล่าสุด" บน Dashboard
--  ต้องรัน s22_part.sql มาก่อน (ตาราง app_flags + plan_last_sync) ถ้ายังไม่เคยรัน
-- ============================================================================

create or replace function public.form_days(p_form text) returns int
language sql immutable as $$ select 4 $$;

drop function if exists public.form_window_ok(date);
drop function if exists public.form_window_ok(date, int);
create or replace function public.form_window_ok(p_date date, p_days int default 4) returns boolean
language sql stable as $$
  select public.is_admin() or (now() at time zone 'Asia/Bangkok')::date between p_date - 1 and p_date + p_days
$$;

create or replace function public.task_check(p_code text, p_key text, p_form text) returns public.plan
language plpgsql stable security definer set search_path = public as $$
declare t public.plan; v_today date := (now() at time zone 'Asia/Bangkok')::date; v_days int := public.form_days(p_form);
begin
  select * into t from public.plan where upper(task_code) = upper(btrim(coalesce(p_code, '')));
  if not found then raise exception 'ไม่พบงานนี้ กรุณาตรวจ Task Code หรือสแกน QR ใหม่'; end if;
  if public.is_canceled(t.status) then raise exception 'งานนี้ถูกยกเลิกแล้ว (%)', t.task_code; end if;
  if v_today > t.date + v_days and not public.is_admin() then
    raise exception 'งานนี้จบแล้ว (งานวันที่ % ลิงก์นี้ใช้ได้ถึงวันที่ %)', to_char(t.date, 'DD/MM/YYYY'), to_char(t.date + v_days, 'DD/MM/YYYY');
  end if;
  if v_today < t.date - 1 and not public.is_admin() then
    raise exception 'ยังไม่ถึงวันงาน (งานวันที่ % เปิดลิงก์ได้ตั้งแต่วันที่ %)', to_char(t.date, 'DD/MM/YYYY'), to_char(t.date - 1, 'DD/MM/YYYY');
  end if;
  return t;
end $$;

create or replace function public.form_submit(p jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  t public.plan; n int; rt boolean; v_note text; v_type text := coalesce(p->>'type', '');
  v_stop int := coalesce(nullif(p->>'stop', '')::int, 0); v_id bigint; v_fin boolean := false; v_now timestamptz := now();
  v_plate text; v_changed boolean; e text[]; ph text[]; pre text; v_last timestamptz; v_ref timestamptz;
  v_dept text; v_have int; v_pend boolean := coalesce((p->>'pending')::boolean, false);
begin
  t := public.task_check(p->>'taskCode', p->>'k', p->>'form');
  pre := t.task_code || '/';
  if (select count(*) from public.road_log where task_code = t.task_code) >= 300 or (select count(*) from public.pickup_log where task_code = t.task_code) >= 100 then
    raise exception 'ส่งข้อมูลของงานนี้ครบจำนวนสูงสุดแล้ว';
  end if;
  n := greatest(1, (t.stop1 <> '')::int + (t.stop2 <> '')::int + (t.stop3 <> '')::int);
  rt := t.round ~ 'กลับ';
  v_note := left(coalesce(p->>'note', ''), 2000);

  if p->>'form' in ('pickup', 'qa') then
    -- รูปส่งงาน WH (pickup.html) / QA (qa.html) : ส่งได้หลายครั้งจนกว่าจะผ่าน 24 ชม. นับจากอัปโหลดครั้งล่าสุดของฝ่ายนั้น รวมไม่เกิน WH 50 / QA 50 รูป
    v_dept := case when p->>'form' = 'qa' then 'QA' else 'WH' end;
    -- งานต่างประเทศ WH : ต้องส่งรูปรถเข้าก่อน ; ส่งรูปส่งงานครั้งแรก = เวลารถออก (จบงาน)
    if v_dept = 'WH' and public.task_intl(t.job_type, t.vehicle_type)
       and not exists (select 1 from public.road_log where task_code = t.task_code and type = 'checkin') then
      raise exception 'กรุณาส่งรูปรถเข้า (หัวข้อ 2) ก่อนส่งรูปส่งงาน';
    end if;
    select max(time) into v_last from public.pickup_log where task_code = t.task_code and source <> 'GPS' and dept = v_dept;
    if v_last is not null and v_now > v_last + interval '24 hours' and not public.is_admin() then
      raise exception 'ปิดรับรูปจาก % แล้ว (เกิน 24 ชม. นับจากอัปโหลดครั้งล่าสุด)', v_dept;
    end if;
    v_have := public.dept_photo_count(t.task_code, v_dept);
    if v_have >= public.dept_photo_max(v_dept, public.task_intl(t.job_type, t.vehicle_type)) then
      raise exception 'ส่งรูปจาก % ครบ % รูปแล้ว ส่งเพิ่มไม่ได้', v_dept, public.dept_photo_max(v_dept, public.task_intl(t.job_type, t.vehicle_type));
    end if;
    ph := public.photo_list(p->'photos', pre, public.dept_photo_max(v_dept, public.task_intl(t.job_type, t.vehicle_type)) - v_have, t.key);
    insert into public.pickup_log (time, task_code, note, photos, dept) values (v_now, t.task_code, v_note, coalesce(ph, '{}'), v_dept) returning id into v_id;
    if v_dept = 'WH' and public.task_intl(t.job_type, t.vehicle_type)
       and not exists (select 1 from public.road_log where task_code = t.task_code and type = 'depart') then
      v_fin := true;
      insert into public.road_log (time, task_code, type, note, finish)
        values (v_now, t.task_code, 'depart', 'WH ต่างประเทศ: รถออก (ส่งรูปส่งงานครั้งแรก)', true);
    end if;

  elsif p->>'form' in ('wh_in', 'wh_out') then
    -- งานต่างประเทศ : WH ส่งรูปรถเข้า (รวมไม่เกิน 20 รูป ส่งเพิ่มได้ภายใน 24 ชม.) ส่งครั้งแรก = เวลารถเข้า
    -- (wh_out = ปุ่มรถออกรุ่นเก่า s18 เก็บไว้กันฟอร์มที่ค้างในมือถือ ; รุ่นนี้รถออก = ส่งรูปส่งงาน WH ครั้งแรก)
    if not public.task_intl(t.job_type, t.vehicle_type) then raise exception 'งานนี้ไม่ใช่งานต่างประเทศ (ประเภทรถ %)', coalesce(nullif(t.vehicle_type, ''), '-'); end if;
    if p->>'form' = 'wh_in' then
      select id, time, cardinality(unload) into v_id, v_ref, v_have from public.road_log where task_code = t.task_code and type = 'checkin' order by id limit 1;
      if v_id is null then
        ph := public.photo_list(p->'unload', pre, 20, t.key);
        insert into public.road_log (time, task_code, type, plate, note, unload)
          values (v_now, t.task_code, 'checkin', t.plate, left('WH ต่างประเทศ: รถเข้า (ส่งรูปรถเข้าครั้งแรก)' || case when v_note <> '' then ' · ' || v_note else '' end, 2000), coalesce(ph, '{}')) returning id into v_id;
      else
        if v_now > v_ref + interval '24 hours' and not public.is_admin() then raise exception 'ปิดรับรูปรถเข้าแล้ว (เกิน 24 ชม. นับจากรถเข้า)'; end if;
        if v_have >= 20 and not v_pend then raise exception 'ส่งรูปรถเข้าครบ 20 รูปแล้ว ส่งเพิ่มไม่ได้'; end if;
        ph := public.photo_list(p->'unload', pre, greatest(0, 20 - v_have), t.key);
        if coalesce(array_length(ph, 1), 0) > 0 then update public.road_log set unload = unload || ph where id = v_id; end if;
      end if;
    else
      if not exists (select 1 from public.road_log where task_code = t.task_code and type = 'checkin') then raise exception 'ยังไม่ได้บันทึกรถเข้า'; end if;
      select id into v_id from public.road_log where task_code = t.task_code and type = 'depart' order by id limit 1;
      if v_id is null then
        v_fin := true;
        insert into public.road_log (time, task_code, type, note, finish)
          values (v_now, t.task_code, 'depart', left('WH ต่างประเทศ: รถออก' || case when v_note <> '' then ' · ' || v_note else '' end, 2000), true) returning id into v_id;
      end if;
    end if;

  elsif p->>'form' = 'driver' then
    if public.task_intl(t.job_type, t.vehicle_type) then raise exception 'งานต่างประเทศ (%) ไม่ใช้ฟอร์มคนขับ : WH บันทึกรถเข้า-ออกในฟอร์มอัปโหลดรูป WH', t.vehicle_type; end if;
    e := array[public.hm(p->'eta'->>0), case when n >= 2 then public.hm(p->'eta'->>1) else '' end, case when n >= 3 then public.hm(p->'eta'->>2) else '' end];
    if v_type = 'checkin' then
      v_plate := public.norm_plate(p->>'plate');
      if v_plate = '' then raise exception 'รูปแบบทะเบียนรถไม่ถูกต้อง ตัวอย่าง: 3 ฒผ 2186'; end if;
      v_changed := v_plate <> t.plate;
      if v_changed then
        update public.plan set plate = v_plate, updated_at = v_now, updated_by = 'ผู้จัดส่ง' where task_code = t.task_code;
        insert into public.edit_log (time, task_code, source, field, old_value, new_value, by_user)
          values (v_now, t.task_code, 'ฟอร์มผู้จัดส่ง (เช็คอิน)', 'ทะเบียนรถ', t.plate, v_plate, 'ผู้จัดส่ง');
      end if;
      insert into public.road_log (time, task_code, type, plate, old_plate, note)
        values (v_now, t.task_code, 'checkin', v_plate, case when v_changed then coalesce(nullif(t.plate, ''), '(ว่าง)') else '' end, v_note) returning id into v_id;
    elsif v_type = 'depart' then
      select id into v_id from public.road_log where task_code = t.task_code and type = 'depart' order by id limit 1;
      if v_id is null then
        insert into public.road_log (time, task_code, type, note) values (v_now, t.task_code, 'depart', v_note) returning id into v_id;
      end if;
    elsif v_type = 'eta' then
      if e[1] || e[2] || e[3] = '' then raise exception 'กรุณาใส่เวลาที่คาดว่าจะถึงอย่างน้อย 1 จุด'; end if;
      insert into public.road_log (time, task_code, type, note, eta1, eta2, eta3)
        values (v_now, t.task_code, 'eta', v_note, e[1], e[2], e[3]) returning id into v_id;
    elsif v_type = 'road' then
      ph := public.photo_list(p->'road', pre, 5, t.key);
      if coalesce(array_length(ph, 1), 0) = 0 and v_note = '' and e[1] || e[2] || e[3] = '' and coalesce((p->>'pending')::boolean, false) = false then
        raise exception 'กรุณาแนบรูปหรือใส่หมายเหตุ';
      end if;
      insert into public.road_log (time, task_code, type, note, eta1, eta2, eta3, road)
        values (v_now, t.task_code, 'road', v_note, e[1], e[2], e[3], coalesce(ph[1:5], '{}')) returning id into v_id;
    elsif v_type in ('arrive', 'unload') then
      if v_stop < 1 or v_stop > n then raise exception 'จุดส่งไม่ถูกต้อง'; end if;
      v_have := public.stop_photo_count(t.task_code, v_stop);                   -- รูปลงงานรวมไม่เกิน 20 รูปต่อจุด
      ph := case when v_type = 'unload' then public.photo_list(p->'unload', pre, greatest(0, 20 - v_have), t.key) else '{}' end;
      v_fin := v_type = 'unload' and v_stop = n and not rt;       -- ลงงานจุดสุดท้าย = จบงาน (งานไป-กลับจบเมื่อรถกลับถึงต้นทาง)
      insert into public.road_log (time, task_code, type, stop, note, unload, finish)
        values (v_now, t.task_code, v_type, v_stop, v_note, coalesce(ph, '{}'), v_fin) returning id into v_id;
    elsif v_type = 'return' then
      if not rt then raise exception 'งานนี้ไม่ใช่รอบไป-กลับ'; end if;
      v_fin := true;
      ph := public.photo_list(p->'unload', pre, greatest(0, 20 - public.stop_photo_count(t.task_code, 0)), t.key);     -- รูปลงงานที่ SCM (ถ้ามี)
      insert into public.road_log (time, task_code, type, note, unload, finish) values (v_now, t.task_code, 'return', v_note, coalesce(ph, '{}'), true) returning id into v_id;
    elsif v_type = 'photo' then
      -- แนบรูปลงงานย้อนหลัง (ฟอร์ม GPS) : จุดที่ v_stop (0 = รูปที่ SCM ตอนกลับถึง) ต้องมีบันทึกถึง/ลงงานแล้ว และยังไม่เกิน 24 ชม.
      v_ref := public.stop_photo_ref(t.task_code, v_stop);
      if v_ref is null then raise exception 'ยังไม่มีบันทึกว่ารถถึงจุดนี้ จึงยังแนบรูปไม่ได้'; end if;
      if v_now > v_ref + interval '24 hours' and not public.is_admin() then raise exception 'ปิดรับรูปจุดนี้แล้ว (เกิน 24 ชม.)'; end if;
      select id into v_id from public.road_log
        where task_code = t.task_code and ((v_stop = 0 and type = 'return') or (v_stop > 0 and stop = v_stop and type in ('arrive', 'unload')))
        order by (type = 'unload') desc, id desc limit 1;
      if v_note <> '' then
        update public.road_log set note = left(case when note = '' then v_note else note || E'\n' || v_note end, 2000) where id = v_id;
      end if;
      v_have := public.stop_photo_count(t.task_code, v_stop);
      if v_have >= 20 and not v_pend and v_note = '' then raise exception 'ส่งรูปจุดนี้ครบ 20 รูปแล้ว ส่งเพิ่มไม่ได้'; end if;
      ph := public.photo_list(p->'unload', pre, greatest(0, 20 - v_have), t.key);
      if coalesce(array_length(ph, 1), 0) > 0 then
        update public.road_log set unload = unload || ph where id = v_id;
      end if;
    else
      raise exception 'ไม่รู้จักประเภทรายการ';
    end if;
  else
    raise exception 'ไม่รู้จักฟอร์ม';
  end if;
  return jsonb_build_object('time', v_now, 'id', v_id, 'taskCode', t.task_code, 'finish', v_fin);
end $$;

create or replace function public.form_attach(p jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare t public.plan; v_id bigint := (p->>'id')::bigint; pre text; cur text[]; add text[]; v_type text; v_stop int; v_ref timestamptz; v_last timestamptz;
  v_dept text; v_other int;
begin
  t := public.task_check(p->>'taskCode', p->>'k', p->>'form');
  pre := t.task_code || '/';
  if p->>'form' in ('pickup', 'qa') then
    select photos, dept into cur, v_dept from public.pickup_log where id = v_id and task_code = t.task_code for update;
    if not found then raise exception 'ไม่พบรายการที่จะแนบรูป'; end if;
    v_other := public.dept_photo_count(t.task_code, v_dept) - cardinality(cur);          -- รวมทุกครั้งของฝ่ายนั้นไม่เกิน WH 50 / QA 50 รูป
    add := public.photo_list(to_jsonb(cur) || coalesce(p->'photos', '[]'::jsonb), pre, greatest(cardinality(cur), public.dept_photo_max(v_dept, public.task_intl(t.job_type, t.vehicle_type)) - v_other), t.key);
    update public.pickup_log set photos = coalesce(add, '{}') where id = v_id;
  else
    select road, type, stop into cur, v_type, v_stop from public.road_log where id = v_id and task_code = t.task_code for update;
    if not found then raise exception 'ไม่พบรายการที่จะแนบรูป'; end if;
    if v_type in ('arrive', 'unload', 'return') then      -- รูปลงงาน : รับได้ถึง 24 ชม. หลังถึง/ลงงานจุดนั้น
      v_ref := public.stop_photo_ref(t.task_code, case when v_type = 'return' then 0 else v_stop end);
      if v_ref is null or (now() > v_ref + interval '24 hours' and not public.is_admin()) then raise exception 'ปิดรับรูปจุดนี้แล้ว (เกิน 24 ชม.)'; end if;
    end if;
    add := public.photo_list(to_jsonb(cur) || coalesce(p->'road', '[]'::jsonb), pre, 5, t.key);
    update public.road_log set road = coalesce(add[1:5], '{}') where id = v_id;
    select unload into cur from public.road_log where id = v_id;
    v_other := case when v_type in ('arrive', 'unload', 'return') then public.stop_photo_count(t.task_code, case when v_type = 'return' then 0 else v_stop end) - cardinality(cur) else 0 end;
    add := public.photo_list(to_jsonb(cur) || coalesce(p->'unload', '[]'::jsonb), pre, greatest(cardinality(cur), 20 - v_other), t.key);
    update public.road_log set unload = coalesce(add, '{}') where id = v_id;
  end if;
  return jsonb_build_object('id', v_id);
end $$;

create or replace function public.plan_update(p_rows jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare r jsonb; v_code text; v_who text; v_now timestamptz := now(); m record; v text; v_old text; d date;
        n_rows int := 0; n_cells int := 0; n_miss int := 0; n_lock int := 0; v_hit boolean; v_status text;
begin
  if not public.can_edit() then raise exception 'FORBIDDEN'; end if;
  select coalesce(nullif(name, ''), email) into v_who from public.profiles where user_id = auth.uid();
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception 'ไม่มีข้อมูล'; end if;
  for r in select * from jsonb_array_elements(p_rows) loop
    v_code := btrim(coalesce(r->>'task_code', ''));
    if v_code = '' then continue; end if;
    select status into v_status from public.plan where task_code = v_code for update;
    if not found then n_miss := n_miss + 1; continue; end if;
    if public.is_canceled(v_status) then n_lock := n_lock + 1; continue; end if;   -- งานที่ยกเลิกแล้วแก้ไม่ได้
    v_hit := false;
    for m in select * from (values
      ('date','date','date','Date'), ('detail','detail','text','Detail'), ('client','client','text','Client Name'), ('job_type','job_type','text','Type'), ('transport','transport','text','Transport'),
      ('schedule','schedule','time','Schedule'), ('arr1','arr1','time','Arrival Time 1'), ('arr2','arr2','time','Arrival Time 2'), ('arr3','arr3','time','Arrival Time 3'),
      ('company','company','text','ชื่อบริษัทขนส่ง'), ('vehicle_type','vehicle_type','text','ประเภทรถ'), ('plate','plate','plate','ทะเบียนรถ'),
      ('driver','driver','text','ชื่อผู้ขับ'), ('phone','phone','text','เบอร์โทรผู้ขับ'), ('round','round','text','รอบขนส่ง'),
      ('stop1','stop1','text','จุดที่ 1'), ('map1','map1','text','Map1'), ('rec1','rec1','text','ชื่อ-เบอร์โทรผู้รับ จุดที่ 1'),
      ('stop2','stop2','text','จุดที่ 2'), ('map2','map2','text','Map2'), ('rec2','rec2','text','ชื่อ-เบอร์โทรผู้รับ จุดที่ 2'),
      ('stop3','stop3','text','จุดที่ 3'), ('map3','map3','text','Map3'), ('rec3','rec3','text','ชื่อ-เบอร์โทรผู้รับ จุดที่ 3'),
      ('status','status','text','Task Status')) f(key, col, kind, label)
    loop
      if not (r ? m.key) then continue; end if;
      v := left(public.blank(r->>m.key), 500);
      if m.kind = 'date' then
        d := public.to_date_loose(r->>m.key);
        if d is null then raise exception 'งาน %: วันที่ไม่ถูกต้อง (%)', v_code, coalesce(r->>m.key, ''); end if;
        v := to_char(d, 'YYYY-MM-DD');
      elsif m.kind = 'time' then
        if v <> '' and public.hm(v) = '' then raise exception 'งาน %: %: รูปแบบเวลาไม่ถูกต้อง (ชม.:นาที)', v_code, m.label; end if;
        v := public.hm(v);
      elsif m.kind = 'plate' and v <> '' then
        v := public.norm_plate(v);
        if v = '' then raise exception 'งาน %: รูปแบบทะเบียนรถไม่ถูกต้อง', v_code; end if;
      end if;
      execute format('select %I::text from public.plan where task_code = $1', m.col) into v_old using v_code;
      if v_old is not distinct from v then continue; end if;
      execute format('update public.plan set %I = $1::%s, updated_at = $2, updated_by = $3 where task_code = $4', m.col, case when m.kind = 'date' then 'date' else 'text' end)
        using v, v_now, v_who, v_code;
      insert into public.edit_log (time, task_code, source, field, old_value, new_value, by_user)
        values (v_now, v_code, 'Excel (Macro)', m.label, coalesce(v_old, ''), v, v_who);
      n_cells := n_cells + 1;
      v_hit := true;
    end loop;
    if v_hit then n_rows := n_rows + 1; end if;
  end loop;
  if n_cells > 0 then      -- s23 : การแก้ไขงานเดิมจาก Excel / บอต ก็นับเป็น "ส่งแผนล่าสุด" (แสดงที่ Dashboard)
    insert into public.app_flags (key, value, at) values ('last_plan_sync', coalesce(v_who, ''), v_now)
    on conflict (key) do update set value = excluded.value, at = excluded.at;
  end if;
  return jsonb_build_object('rows', n_rows, 'cells', n_cells, 'missing', n_miss, 'locked', n_lock);
end $$;
