use std::cmp::Ordering;
use rand::prelude::*;
use rand_pcg::Pcg64;

static mut CMPS: u32 = 0;
static mut PODS: u32 = 0;

#[derive(Debug)]
pub enum Order{
    Random,
    Sorted,
    Reverse
}

pub fn gen_list(n: u32, order: Order) -> Vec<u32>{
    let mut rng: Pcg64 = Pcg64::from_entropy();
    let mut vector: Vec<u32> = Vec::new();
    for _ in 0..n {
        vector.push(rng.gen_range(0..2*n));
    }
    match order {
        Order::Random => vector,
        Order::Sorted => {
            vector.sort();
            vector
        },
        Order::Reverse => {
            vector.sort();
            vector.reverse();
            vector
        },
    }
}

#[derive(Debug, Clone)]
struct BstNode {
    value: u32,
    left: Option<Box<BstNode>>,
    right: Option<Box<BstNode>>,
}

impl BstNode {
    fn new(value: u32) -> Self {
        BstNode {
            value,
            left: None,
            right: None,
        }
    }

    fn search(&self, value: u32) -> bool {
        if self.value == value {
            return true;
        }
        if value < self.value {
            if let Some(left) = &self.left {
                left.search(value)
            } else {
                false
            }
        } else if let Some(right) = &self.right {
            return right.search(value);
        } else {
            false
        }
    }

    fn insert(&mut self, value: u32) {
        match value.cmp(&self.value) {
            Ordering::Less => {
                unsafe{ CMPS += 1 }
                unsafe{ PODS += 1 }
                if let Some(ref mut left) = self.left {
                    left.insert(value);
                } else {
                    self.left = Some(Box::new(BstNode::new(value)));
                }
            }
            Ordering::Greater => {
                unsafe{ CMPS += 2 }
                unsafe{ PODS += 1 }
                if let Some(ref mut right) = self.right {
                    right.insert(value);
                } else {
                    self.right = Some(Box::new(BstNode::new(value)));
                }
            }
            Ordering::Equal => {unsafe{ CMPS += 2 }}
        }
    }
 
    fn height(&self) -> u32 {
        let left_height = match &self.left {
            Some(left) => left.height(),
            None => 0,
        };
        let right_height = match &self.right {
            Some(right) => right.height(),
            None => 0,
        };
        1 + std::cmp::max(left_height, right_height)
    }

    fn print_node(&self, prefix: &str, is_left: bool) {
        let side = if is_left { "└──" } else { "├──" };
        println!("{}{} {}", prefix, side, self.value);
    }

    fn print_tree_helper(&self, prefix: &str, is_left: bool) {
        if let Some(right) = self.right.as_ref() {
            right.print_tree_helper(&format!("{}{}   ", prefix, if is_left { "│" } else { " " }), false);
        }
        self.print_node(prefix, is_left);
        if let Some(left) = self.left.as_ref() {
            left.print_tree_helper(&format!("{}{}   ", prefix, if is_left { " " } else { "│" }), true);
        }
    }

    fn delete(mut this: Box<BstNode>, target: &u32) -> Option<Box<BstNode>> {
        unsafe{ CMPS += 1 }
        if target < &this.value {
            unsafe{ PODS += 1 }
            if let Some(left) = this.left.take() {
                unsafe{ PODS += 1 }
                this.left = Self::delete(left, target);
            }
            return Some(this);
        }

        unsafe{ CMPS += 1 }
        if target > &this.value {
            unsafe{ PODS += 1 }
            if let Some(right) = this.right.take() {
                unsafe{ PODS += 1 }
                this.right = Self::delete(right, target);
            }
            return Some(this);
        }
        unsafe{ PODS += 3 }
        match (this.left.take(), this.right.take()) {
            (None, None) => None,
            (Some(left), None) => Some(left),
            (None, Some(right)) => Some(right),
            (Some(mut left), Some(right)) => {
                if let Some(mut rightmost) = left.rightmost_child() {
                    unsafe{ PODS += 2 }
                    rightmost.left = Some(left);
                    rightmost.right = Some(right);
                    Some(rightmost)
                } else {
                    unsafe{ PODS += 1 }
                    left.right = Some(right);
                    Some(left)
                }
            },
        }
    }

    fn rightmost_child(&mut self) -> Option<Box<BstNode>> {
        unsafe{ PODS += 1 }
        match self.right {
            Some(ref mut right) => {
                if let Some(t) = right.rightmost_child() {
                    Some(t)
                } else {
                    let mut r = self.right.take();
                    if let Some(ref mut r) = r {
                        unsafe{ PODS += 1 }
                        self.right = std::mem::replace(&mut r.left, None);
                    }
                    r
                }
            },
            None => None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct BinarySearchTree {
    root: Option<Box<BstNode>>,
}

impl Default for BinarySearchTree {
    fn default() -> Self {
        Self::new()
    }
}

impl BinarySearchTree {
    pub fn new() -> Self {
        BinarySearchTree { root: None }
    }

    pub fn insert(&mut self, value: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if let Some(ref mut root) = self.root {
            root.insert(value);
        } else {
            self.root = Some(Box::new(BstNode::new(value)));
        }
    }

    pub fn delete(&mut self, target: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if let Some(root) = self.root.take() {
            self.root = BstNode::delete(root, &target);
        }
    }

    pub fn height(&self) -> u32 {
        match &self.root {
            Some(root) => root.height(),
            None => 0,
        }
    }

    pub fn print(&self) {
        if let Some(ref node) = self.root {
            node.print_tree_helper("", false);
        }
    }

    pub fn search(&self, value: u32) -> bool {
        if let Some(root) = &self.root {
            root.search(value)
        } else {
            false
        }
    }
}

#[derive(Debug, Clone, PartialEq, Copy)]
enum Color {
    Red,
    Black,
}

#[derive(Debug, Clone)]
struct RBNode {
    value: u32,
    color: Color,
    left: Option<Box<RBNode>>,
    right: Option<Box<RBNode>>,
}

impl RBNode {
    fn new(value: u32) -> Self {
        RBNode {
            value,
            color: Color::Red,
            left: None,
            right: None,
        }
    }

    fn is_red(&self) -> bool {
        self.color == Color::Red
    }

    fn rotate_left(mut self: Box<Self>) -> Box<Self> {
        let mut x = self.right.take().unwrap();
        unsafe{ PODS += 1 }
        self.right = x.left.take();
        x.left = Some(self);
        x.color = x.left.as_ref().unwrap().color;
        x.left.as_mut().unwrap().color = Color::Red;
        x
    }

    fn rotate_right(mut self: Box<Self>) -> Box<Self> {
        let mut x = self.left.take().unwrap();
        unsafe{ PODS += 1 }
        self.left = x.right.take();
        x.right = Some(self);
        x.color = x.right.as_ref().unwrap().color;
        x.right.as_mut().unwrap().color = Color::Red;
        x
    }

    fn flip_colors(mut self: Box<Self>) -> Box<Self> {
        unsafe{ PODS += 1 }
        self.color = Color::Red;
        unsafe{ PODS += 1 }
        self.left.as_mut().unwrap().color = Color::Black;
        unsafe{ PODS += 1 }
        self.right.as_mut().unwrap().color = Color::Black;
        self
    }

    fn balance(mut self: Box<Self>) -> Box<Self> {
        if self.right.as_ref().map_or(false, |x| x.is_red()) {
            unsafe{ PODS += 1 }
            self = self.rotate_left();
        }
        if self.left.as_ref().map_or(false, |x| x.left.as_ref().map_or(false, |y| y.is_red())) {
            unsafe{ PODS += 1 }
            self = self.rotate_right();
        }
        if self.left.as_ref().map_or(false, |x| x.is_red()) && self.right.as_ref().map_or(false, |x| x.is_red()) {
            unsafe{ PODS += 1 }
            self = self.flip_colors();
        }
        self
    }

    fn insert(mut self: Box<Self>, value: u32) -> Box<Self> {
        match value.cmp(&self.value) {
            Ordering::Less => {
                unsafe{ CMPS += 1 }
                if self.left.is_none() {
                    unsafe{ PODS += 1 }
                    self.left = Some(Box::new(RBNode::new(value)));
                } else {
                    unsafe{ PODS += 1 }
                    self.left = Some(self.left.unwrap().insert(value));
                }
            },
            Ordering::Greater => {
                unsafe{ CMPS += 2 }
                if self.right.is_none() {
                    unsafe{ PODS += 1 }
                    self.right = Some(Box::new(RBNode::new(value)));
                } else {
                    unsafe{ PODS += 1 }
                    self.right = Some(self.right.unwrap().insert(value));
                }
            },
            Ordering::Equal => {unsafe{ CMPS += 2 }},
        }
        unsafe{ PODS += 1 }
        self = self.balance();
        self
    }

    fn find_min_node(&mut self) -> Box<Self> {
        if let Some(left) = self.left.as_mut() {
            if left.left.is_none() {
                return self.left.take().unwrap();
            }
            return left.find_min_node();
        }
        Box::new(self.clone())
    }

    fn delete(mut self: Box<Self>, value: u32) -> Option<Box<Self>> {
        match value.cmp(&self.value) {
            Ordering::Less => {
                unsafe{ CMPS += 1 }
                if self.left.is_some() {
                    unsafe{ PODS += 2 }
                    let left = self.left.take().unwrap();
                    unsafe{ PODS += 1 }
                    self.left = left.delete(value);
                }
            }
            Ordering::Greater => {
                unsafe{ CMPS += 2 }
                if self.right.is_some() {
                    unsafe{ PODS += 2 }
                    let right = self.right.take().unwrap();
                    unsafe{ PODS += 1 }
                    self.right = right.delete(value);
                }
            }
            Ordering::Equal => {
                unsafe{ CMPS += 2 }
                if self.right.is_none() {
                    unsafe{ PODS += 1 }
                    return self.left;
                } else if self.left.is_none() {
                    unsafe{ PODS += 2 }
                    return self.right;
                } else {
                    unsafe{ PODS += 2 }
                    let mut right = self.right.take().unwrap();
                    let min_node = right.find_min_node();
                    self.value = min_node.value;
                    unsafe{ PODS += 1 }
                    self.right = right.delete(min_node.value);
                }
            }
        }
        Some(self.balance())
    }

    fn height(&self) -> u32 {
        let left_height = self.left.as_ref().map_or(0, |node| node.height());
        let right_height = self.right.as_ref().map_or(0, |node| node.height());
        1 + std::cmp::max(left_height, right_height)
    }

    fn print_node(&self, prefix: &str, is_left: bool) {
        let side = if is_left { "└──" } else { "├──" };
        println!("{}{} {}", prefix, side, self.value);
    }

    fn print_tree_helper(&self, prefix: &str, is_left: bool) {
        if let Some(right) = self.right.as_ref() {
            right.print_tree_helper(&format!("{}{}   ", prefix, if is_left { "│" } else { " " }), false);
        }
        self.print_node(prefix, is_left);
        if let Some(left) = self.left.as_ref() {
            left.print_tree_helper(&format!("{}{}   ", prefix, if is_left { " " } else { "│" }), true);
        }
    }
}

#[derive(Debug, Clone)]
pub struct RBTree{
    root: Option<Box<RBNode>>,
}

impl Default for RBTree {
    fn default() -> Self {
        Self::new()
    }
}

impl RBTree {
    pub fn new() -> Self {
        RBTree { root: None }
    }

    pub fn insert(&mut self, value: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if self.root.is_none() {
            self.root = Some(Box::new(RBNode::new(value)));
            self.root.as_mut().unwrap().color = Color::Black;
            return;
        }
        let after_ins = self.root.as_ref().unwrap().clone().insert(value);
        self.root = Some(after_ins);
        self.root.as_mut().unwrap().color = Color::Black;
    }

    pub fn delete(&mut self, value: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if self.root.is_none() {
            return;
        }
        let after_del = self.root.take().unwrap().delete(value);
        self.root = after_del;
        if let Some(root) = self.root.as_mut() {
            root.color = Color::Black;
        }
    }

    pub fn height(&self) -> u32 {
        self.root.as_ref().map_or(0, |node| node.height())
    }

    pub fn print_tree(&self) {
        if let Some(root) = self.root.as_ref() {
            root.print_tree_helper("", false);
        }
    }
}

#[derive(Debug, Clone)]
struct SplayNode {
    value: u32,
    left: Option<Box<SplayNode>>,
    right: Option<Box<SplayNode>>,
}


impl SplayNode {
    fn new(value: u32) -> Self {
        SplayNode {
            value,
            left: None,
            right: None,
        }
    }

    fn rotate_right(mut self: Box<Self>) -> Box<Self> {
        unsafe{ PODS += 1 }
        if self.left.is_some() {
            unsafe{ PODS += 1 }
            let mut x = self.left.take().unwrap();
            unsafe{ PODS += 1 }
            self.left = x.right.take();
            x.right = Some(self);
            return x;
        }
        self
    }

    fn rotate_left(mut self: Box<Self>) -> Box<Self> {
        unsafe{ PODS += 1 }
        if self.right.is_some() {
            unsafe{ PODS += 1 }
            let mut x = self.right.take().unwrap();
            unsafe{ PODS += 1 }
            self.right = x.left.take();
            x.left = Some(self);
            return x;
        }
        self
    }

    fn splay(mut self: Box<Self>, value: u32) -> Box<Self> {
        unsafe{ CMPS += 2 }
        if value < self.value {
            unsafe{ CMPS -= 1 }
            unsafe{ PODS += 1 }
            if let Some(ref mut left) = self.left {
                unsafe{ CMPS += 2 }
                if value < left.value {
                    unsafe{ CMPS -= 1 }
                    // Zig-Zig
                    unsafe{ PODS += 1 }
                    left.left = left.left.take().map(|node| node.splay(value));
                    self = self.rotate_right();
                } else if value > left.value {
                    // Zig-Zag4
                    unsafe{ PODS += 1 }
                    left.right = left.right.take().map(|node| node.splay(value));
                    self.left = self.left.map(|node| node.rotate_left());
                }
                if let Some(ref mut _left) = self.left {
                    unsafe{ PODS += 1 }
                    self = self.rotate_right();
                }
            }
        } else if value > self.value {
            if let Some(ref mut right) = self.right {
                unsafe{ CMPS += 2 }
                if value > right.value {
                    unsafe{ CMPS -= 1 }
                    // Zag-Zag
                    unsafe{ PODS += 1 }
                    right.right = right.right.take().map(|node| node.splay(value));
                    self = self.rotate_left();
                } else if value < right.value {
                    // Zag-Zig
                    unsafe{ PODS += 1 }
                    right.left = right.left.take().map(|node| node.splay(value));
                    self.right = self.right.map(|node| node.rotate_right());
                }
                if let Some(ref mut _right) = self.right {
                    unsafe{ PODS += 1 }
                    self = self.rotate_left();
                }
            }
        }
        self
    }

    fn insert(mut self: Box<Self>, value: u32) -> Box<Self> {
        unsafe{ CMPS += 2 }
        if value < self.value {
            unsafe{ CMPS -= 1 }
            unsafe{ PODS += 1 }
            if let Some(left) = self.left.take() {
                unsafe{ PODS += 1 }
                self.left = Some(left.insert(value));
            } else {
                unsafe{ PODS += 1 }
                self.left = Some(Box::new(SplayNode::new(value)));
            }
        } else if value > self.value {
            unsafe{ PODS += 1 }
            if let Some(right) = self.right.take() {
                self.right = Some(right.insert(value));
                unsafe{ PODS += 1 }
            } else {
                self.right = Some(Box::new(SplayNode::new(value)));
                unsafe{ PODS += 1 }
            }
        }
        self.splay(value)
    }

    
    fn delete(mut self: Box<Self>, value: u32) -> Option<Box<Self>> {
        self = self.splay(value);
        unsafe{ PODS += 1 }
        unsafe{ CMPS += 1 }
        if value != self.value {
            return Some(self);
        }

        unsafe{ PODS += 2 }
        match (self.left.take(), self.right.take()) {
            (None, right) => right,
            (left, None) => left,
            (Some(left), Some(right)) => {
                let mut x = right.splay(value);
                x.left = Some(left);
                Some(x)
            }
        }
    }

    
    fn height(&self) -> u32 {
        let left_height = self.left.as_ref().map_or(0, |node| node.height());
        let right_height = self.right.as_ref().map_or(0, |node| node.height());
        1 + std::cmp::max(left_height, right_height)
    }

    
    fn print_node(&self, prefix: &str, is_left: bool) {
        let side = if is_left { "└──" } else { "├──" };
        println!("{}{} {}", prefix, side, self.value);
    }

    
    fn print_tree_helper(&self, prefix: &str, is_left: bool) {
        if let Some(right) = self.right.as_ref() {
            right.print_tree_helper(&format!("{}{}   ", prefix, if is_left { "│" } else { " " }), false);
        }
        self.print_node(prefix, is_left);
        if let Some(left) = self.left.as_ref() {
            left.print_tree_helper(&format!("{}{}   ", prefix, if is_left { " " } else { "│" }), true);
        }
    }
}

#[derive(Debug, Clone)]
pub struct SplayTree {
    root: Option<Box<SplayNode>>,
}

impl Default for SplayTree {
    fn default() -> Self {
        Self::new()
    }
}

impl SplayTree {
    pub fn new() -> Self {
        SplayTree { root: None }
    }

    pub fn insert(&mut self, value: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if let Some(root) = self.root.take() {
            self.root = Some(root.insert(value));
        } else {
            self.root = Some(Box::new(SplayNode::new(value)));
        }
    }

    pub fn height(&self) -> u32 {
        self.root.as_ref().map_or(0, |node| node.height())
    }

    pub fn print_tree(&self) {
        if let Some(root) = self.root.as_ref() {
            root.print_tree_helper("", false);
        }
    }

    pub fn delete(&mut self, value: u32) {
        unsafe{
            CMPS = 0;
            PODS = 0;
        }
        if let Some(root) = self.root.take() {
            self.root = root.delete(value);
        }
    }
}

pub fn get_cmps() -> u32 {
    unsafe { CMPS }
}

pub fn get_pods() -> u32 {
    unsafe { PODS }
}
