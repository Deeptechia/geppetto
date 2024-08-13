## LLM Handler


## Object variables

- name = "Name of the model"
- model = "Model that will be used"
- client = "Api client"

## Functions

### get_info(self)

Returns the information of the model.

### llm_generate_content(self, prompt: str, callback: Callable, *callback_args)

It is an abstract method. It should be implemented in the child class.

### get_prompt_from_thread(self, thread: List[Dict], assistant_tag: str, user_tag: str)

Get the prompt from the thread.

### split_message(self, message)

Split a message into parts if it exceeds 4000 characters.


