use rand::Rng;
use rand::thread_rng;
use rand::seq::SliceRandom;
//use std::thread;
use std::time::Instant;

fn is_sorted<T>(data: &[T]) -> bool
where
    T: Ord,
{
    data.windows(2).all(|w| w[0] <= w[1])
}

fn main() {
    println!("Enter array length:");
    let mut input = String::new();
    let mut steps: u128 = 0;
    std::io::stdin().read_line(&mut input).expect("Failed to read line");
    let n: usize = match input.trim().parse() {
        Ok(num) => num,
        Err(_) => panic!("crash and burn"),
    };
    let mut array : Vec<u32> = (1..=n as u32).collect();
    array.shuffle(&mut thread_rng());
    println!("Array created: {:?}", &array);
    let now = Instant::now();
    // thread::spawn(|| {
    //     while !is_sorted(&array) {
    //         print!("{:?} {}\r", &array, &steps);
    //     }
    // });
    while !is_sorted(&array) {
        let x = thread_rng().gen_range(0..=n-1);
        let y = thread_rng().gen_range(0..=n-1);
        let z = array[x];
        array[x] = array[y];
        array[y] = z;
        steps += 1;
    }
    let elapsed_time = now.elapsed();
    let elapsed_secs: f64 = elapsed_time.as_nanos() as f64/1_000_000_000.0;
    println!("Done: {:?}\nSteps: {}\nEslaped: {:?}\nSpeed: {} steps/second", &array, &steps, &elapsed_time, steps as f64/&elapsed_secs);
}

// TODO: print info while in process
// TODO: print stats after ^C