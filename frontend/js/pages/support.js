// Support: a message to the owner (something broken, wrong class info, a
// missing class, an idea). Links from a class fill in the course and section:
//   support.html?kind=wrong_info&course=SOC%20101&section=5
// Only the kind of message is counted, never what was typed.

import "../nav.js";
import { busy, counter, sendForm } from "../feedback.js";
import { $, signal } from "../ui.js";

const MESSAGE_MIN = 10;
const MESSAGE_MAX = 2000;
const form = $("#support-form");
const status = $("#support-status");
const sendButton = $("#support-send");
const { kind, message, course, section, email } = form.elements;

// prefill from the link (values go into form fields, never into the page as HTML)
const params = new URLSearchParams(location.search);
if ([...kind.options].some((o) => o.value === params.get("kind"))) kind.value = params.get("kind");
if (params.get("course")) course.value = params.get("course").slice(0, 20);
if (params.get("section")) section.value = params.get("section").slice(0, 10);

const updateCount = counter(message, $("#support-count"), MESSAGE_MAX);

function say(text, isError) {
  status.textContent = text;
  status.classList.toggle("is-error", Boolean(isError));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (sendButton.disabled) return;
  const text = message.value.trim();
  if (text.length < MESSAGE_MIN) { say(`Please tell us a bit more (at least ${MESSAGE_MIN} characters).`, true); message.focus(); return; }
  if (text.length > MESSAGE_MAX) { say(`Your message can be at most ${MESSAGE_MAX} characters.`, true); message.focus(); return; }
  const mail = email.value.trim();
  if (mail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) { say("That email doesn't look right. You can also leave it empty.", true); email.focus(); return; }
  busy(sendButton, true, "Send message");
  say("", false);
  try {
    const sentKind = kind.value;
    const answer = await sendForm("/api/support", form, {
      kind: sentKind, message: text, course: course.value.trim(), section: section.value.trim(), email: mail,
    });
    form.reset();
    updateCount();
    say(`Got it. We read every message. Your reference: ${answer.ref}`, false);
    signal("support_submit", { kind: sentKind });
  } catch (err) {
    say(err.message, true);
  } finally {
    busy(sendButton, false, "Send message");
  }
});
