use std::collections::HashMap;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ResourceType {
    CPU,
    Memory,
    GPU,
    Network,
}

pub fn schedule_jobs(
    resources: Vec<(ResourceType, u64)>,
    job_requests: Vec<(u32, Vec<(ResourceType, u64)>, u64)>
) -> Vec<u32> {
    let mut available: HashMap<ResourceType, u64> = HashMap::new();
    for (rtype, cap) in resources {
        available.insert(rtype, cap);
    }

    let mut scheduled = Vec::new();

    for (job_id, reqs, deadline) in job_requests {
        if deadline < 1 {
            continue;
        }
        let mut can_schedule = true;
        for &(rtype, amount) in &reqs {
            let avail = available.get(&rtype).copied().unwrap_or(0);
            if avail < amount {
                can_schedule = false;
                break;
            }
        }
        if can_schedule {
            for (rtype, amount) in reqs {
                if let Some(v) = available.get_mut(&rtype) {
                    *v -= amount;
                }
            }
            scheduled.push(job_id);
        }
    }
    scheduled
}