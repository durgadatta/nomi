use std::fmt;

#[derive(Debug)]
pub(crate) struct ParseError {
    pub(crate) message: String,
    pub(crate) offset: usize,
}

impl ParseError {
    pub(crate) fn new(message: impl Into<String>, offset: usize) -> Self {
        Self {
            message: message.into(),
            offset,
        }
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} at byte {}", self.message, self.offset)
    }
}
