-- s24 : Delay Trend คิด % ต่องานแล้วเฉลี่ย + ถึงช้าไม่เกิน 15 นาทีนับเป็นทันเวลา (รันซ้ำได้)
insert into public.eta_config (key, value, note) values ('delay_grace_min', '15', 'Delay Trend : ถึงช้ากว่าเวลานัดไม่เกินกี่นาทีถือว่า "ทันเวลา" (15 = สายไม่เกิน 15 นาทียังนับเป็นทัน)')
on conflict (key) do update set value = '15', note = excluded.note;

create or replace function public.delay_trend(p_from date, p_to date, p_group text default 'day') returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare grace double precision := public.cfgn('delay_grace_min', 15);
begin
  if not public.is_member() then raise exception 'FORBIDDEN'; end if;
  if p_from is null or p_to is null or p_to < p_from or p_to - p_from > 800 then raise exception 'BAD_RANGE'; end if;
  -- % ทันเวลา = คิดแต่ละงาน (จุดที่ทัน / จุดทั้งหมดของงานนั้น) แล้วเฉลี่ยทุกงานในช่วง ; ถึงช้าไม่เกิน delay_grace_min นาทีนับเป็นทัน
  -- any_late = จำนวนจุดที่ช้ากว่าเวลานัดแม้แต่นาทีเดียว (ใช้ตัดสินสีแท่ง : เขียว = ไม่มีสายเลย)
  return coalesce((select jsonb_agg(jsonb_build_object(
      'period', s.period, 'n', s.n, 'ontime', s.ontime, 'late', s.n - s.ontime, 'tasks', k.tasks,
      'ontime_pct', round(k.pct::numeric, 1), 'pct_sum', round(k.pct_sum::numeric, 3), 'any_late', s.any_late,
      'avg_diff', round(s.avg_diff::numeric, 1), 'avg_late', round(s.avg_late::numeric, 1), 'max_late', s.max_late, 'gps', s.gps) order by s.period)
    from (select r.period, count(*) as n, count(*) filter (where r.diff_min <= grace) as ontime, count(*) filter (where r.diff_min > 0) as any_late,
                 avg(r.diff_min) as avg_diff, avg(r.diff_min) filter (where r.diff_min > grace) as avg_late, max(r.diff_min) filter (where r.diff_min > grace) as max_late,
                 count(*) filter (where r.source = 'GPS') as gps
          from (select case when p_group = 'month' then to_char(x.task_date, 'YYYY-MM') else to_char(x.task_date, 'YYYY-MM-DD') end as period, x.* from public.delay_rows(p_from, p_to) x) r group by 1) s
    join (select q.period, count(*) as tasks, avg(100.0 * q.ok / q.n) as pct, sum(100.0 * q.ok / q.n) as pct_sum
          from (select case when p_group = 'month' then to_char(x.task_date, 'YYYY-MM') else to_char(x.task_date, 'YYYY-MM-DD') end as period, x.task_code,
                       count(*) as n, count(*) filter (where x.diff_min <= grace) as ok
                from public.delay_rows(p_from, p_to) x group by 1, 2) q group by 1) k on k.period = s.period), '[]'::jsonb);
end $$;
