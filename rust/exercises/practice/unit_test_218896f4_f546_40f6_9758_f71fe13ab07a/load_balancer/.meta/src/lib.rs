use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RequestStatus {
    Queued,
    Processing(u32),
    Completed,
}

#[derive(Debug)]
struct RequestInfo {
    id: u32,
    processing_units: u32,
    status: RequestStatus,
}

#[derive(Debug)]
struct Server {
    id: u32,
    capacity: u32,
    current_load: u32,
    available: bool,
    assigned_requests: Vec<u32>,
}

pub struct LoadBalancer {
    servers: HashMap<u32, Server>,
    requests: HashMap<u32, RequestInfo>,
    request_queue: Vec<u32>,
}

impl LoadBalancer {
    pub fn new() -> Self {
        LoadBalancer {
            servers: HashMap::new(),
            requests: HashMap::new(),
            request_queue: Vec::new(),
        }
    }

    pub fn add_server(&mut self, server_id: u32, capacity: u32) {
        self.servers.insert(
            server_id,
            Server {
                id: server_id,
                capacity,
                current_load: 0,
                available: true,
                assigned_requests: Vec::new(),
            },
        );
        self.dispatch_requests();
    }

    pub fn remove_server(&mut self, server_id: u32) {
        if let Some(server) = self.servers.get_mut(&server_id) {
            server.available = false;
            server.current_load = 0;
            let requests_to_reassign = server.assigned_requests.clone();
            for req_id in requests_to_reassign {
                if let Some(req) = self.requests.get_mut(&req_id) {
                    req.status = RequestStatus::Queued;
                    self.request_queue.push(req_id);
                }
            }
            server.assigned_requests.clear();
        }
        self.dispatch_requests();
    }

    pub fn recover_server(&mut self, server_id: u32) {
        if let Some(server) = self.servers.get_mut(&server_id) {
            server.available = true;
        }
        self.dispatch_requests();
    }

    pub fn new_request(&mut self, request_id: u32, processing_units: u32) {
        let req = RequestInfo {
            id: request_id,
            processing_units,
            status: RequestStatus::Queued,
        };
        self.requests.insert(request_id, req);
        self.request_queue.push(request_id);
        self.dispatch_requests();
    }

    pub fn complete_request(&mut self, request_id: u32) {
        if let Some(req) = self.requests.get_mut(&request_id) {
            if let RequestStatus::Processing(server_id) = req.status {
                if let Some(server) = self.servers.get_mut(&server_id) {
                    if server.current_load >= req.processing_units {
                        server.current_load -= req.processing_units;
                    } else {
                        server.current_load = 0;
                    }
                    server.assigned_requests.retain(|&id| id != request_id);
                }
                req.status = RequestStatus::Completed;
            }
        }
        self.dispatch_requests();
    }

    pub fn get_server_loads(&self) -> Vec<(u32, u32)> {
        let mut loads = Vec::new();
        for server in self.servers.values() {
            if server.available {
                loads.push((server.id, server.current_load));
            }
        }
        loads
    }

    pub fn get_request_status(&self, request_id: u32) -> RequestStatus {
        if let Some(req) = self.requests.get(&request_id) {
            req.status.clone()
        } else {
            RequestStatus::Queued
        }
    }

    fn dispatch_requests(&mut self) {
        self.request_queue.sort_by_key(|req_id| {
            self.requests.get(req_id).map(|r| r.processing_units).unwrap_or(0)
        });
        let mut i = 0;
        while i < self.request_queue.len() {
            let req_id = self.request_queue[i];
            let req = match self.requests.get(&req_id) {
                Some(r) => r,
                None => {
                    i += 1;
                    continue;
                }
            };
            let mut candidate: Option<(u32, u32)> = None;
            for server in self.servers.values() {
                if server.available && (server.capacity >= server.current_load + req.processing_units) {
                    match candidate {
                        None => candidate = Some((server.id, server.current_load)),
                        Some((_, cand_load)) => {
                            if server.current_load < cand_load {
                                candidate = Some((server.id, server.current_load));
                            }
                        }
                    }
                }
            }
            if let Some((server_id, _)) = candidate {
                if let Some(server) = self.servers.get_mut(&server_id) {
                    server.current_load += req.processing_units;
                    server.assigned_requests.push(req_id);
                }
                if let Some(req_mut) = self.requests.get_mut(&req_id) {
                    req_mut.status = RequestStatus::Processing(server_id);
                }
                self.request_queue.remove(i);
            } else {
                i += 1;
            }
        }
    }
}