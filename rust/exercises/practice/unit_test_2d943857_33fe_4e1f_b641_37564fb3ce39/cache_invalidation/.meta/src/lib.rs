use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};
use std::time::{Instant, Duration};

const TTL_MS: u128 = 100;

struct CachedEntry {
    content: String,
    timestamp: Instant,
}

impl CachedEntry {
    fn new(content: String) -> Self {
        CachedEntry {
            content,
            timestamp: Instant::now(),
        }
    }

    fn is_valid(&self) -> bool {
        self.timestamp.elapsed().as_millis() <= TTL_MS
    }
}

static DB: OnceLock<Mutex<HashMap<i32, String>>> = OnceLock::new();
static CACHE: OnceLock<Mutex<HashMap<i32, CachedEntry>>> = OnceLock::new();

fn get_db() -> &'static Mutex<HashMap<i32, String>> {
    DB.get_or_init(|| Mutex::new(HashMap::new()))
}

fn get_cache() -> &'static Mutex<HashMap<i32, CachedEntry>> {
    CACHE.get_or_init(|| Mutex::new(HashMap::new()))
}

/// Updates a post in the database and propagates the invalidation message to the cache nodes
/// based on the specified strategy ("write-through" or "write-invalidate").
pub fn UpdatePost(post_id: i32, content: String, strategy: String) -> Result<(), String> {
    match strategy.as_str() {
        "write-through" => {
            {
                let mut cache = get_cache().lock().map_err(|_| "Cache lock poisoned".to_string())?;
                cache.insert(post_id, CachedEntry::new(content.clone()));
            }
            let mut db = get_db().lock().map_err(|_| "DB lock poisoned".to_string())?;
            db.insert(post_id, content);
            Ok(())
        },
        "write-invalidate" => {
            {
                let mut db = get_db().lock().map_err(|_| "DB lock poisoned".to_string())?;
                db.insert(post_id, content.clone());
            }
            {
                let mut cache = get_cache().lock().map_err(|_| "Cache lock poisoned".to_string())?;
                cache.remove(&post_id);
            }
            Ok(())
        },
        _ => Err("Unknown strategy".to_string()),
    }
}

/// Retrieves a post from the cache. If the post is not in the cache or the entry has expired,
/// it retrieves the post from the database, caches it, and returns it.
pub fn GetPost(post_id: i32) -> Result<String, String> {
    {
        let mut cache = get_cache().lock().map_err(|_| "Cache lock poisoned".to_string())?;
        if let Some(entry) = cache.get(&post_id) {
            if entry.is_valid() {
                return Ok(entry.content.clone());
            } else {
                cache.remove(&post_id);
            }
        }
    }
    let content = {
        let db = get_db().lock().map_err(|_| "DB lock poisoned".to_string())?;
        db.get(&post_id).cloned().unwrap_or_else(|| "".to_string())
    };
    {
        let mut cache = get_cache().lock().map_err(|_| "Cache lock poisoned".to_string())?;
        cache.insert(post_id, CachedEntry::new(content.clone()));
    }
    Ok(content)
}