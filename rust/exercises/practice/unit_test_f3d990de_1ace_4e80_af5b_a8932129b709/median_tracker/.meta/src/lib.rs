use std::collections::BTreeMap;

pub struct MedianTracker {
    // Using BTreeMap to store frequency of numbers
    numbers: BTreeMap<i64, usize>,
    // Total count of numbers
    count: usize,
}

impl MedianTracker {
    pub fn new() -> Self {
        MedianTracker {
            numbers: BTreeMap::new(),
            count: 0,
        }
    }

    pub fn insert(&mut self, num: i64) {
        *self.numbers.entry(num).or_insert(0) += 1;
        self.count += 1;
    }

    pub fn remove(&mut self, num: i64) {
        if let Some(freq) = self.numbers.get_mut(&num) {
            if *freq > 0 {
                *freq -= 1;
                self.count -= 1;
                if *freq == 0 {
                    self.numbers.remove(&num);
                }
            }
        }
    }

    pub fn get_median(&self) -> Option<f64> {
        if self.count == 0 {
            return None;
        }

        // If count is odd, we need the (count+1)/2 th element
        // If count is even, we need the average of count/2 th and (count/2 + 1) th elements
        let is_odd = self.count % 2 == 1;
        let mid = (self.count + 1) / 2;

        let mut current_count = 0;
        let mut first_median = None;
        let mut second_median = None;

        for (&num, &freq) in self.numbers.iter() {
            current_count += freq;
            
            if first_median.is_none() && current_count >= mid {
                first_median = Some(num);
            }
            
            if !is_odd && first_median.is_some() && second_median.is_none() && current_count >= mid + 1 {
                second_median = Some(num);
                break;
            }
            
            if is_odd && first_median.is_some() {
                break;
            }
        }

        match (first_median, second_median) {
            (Some(m1), Some(m2)) => Some((m1 as f64 + m2 as f64) / 2.0),
            (Some(m1), None) => Some(m1 as f64),
            _ => None,
        }
    }
}