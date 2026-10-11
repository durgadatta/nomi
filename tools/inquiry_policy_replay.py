"""Independent cost-bound replay over independently verified query branches."""

from fractions import Fraction as F

from tools import adaptive_inquiry_replay as observations
from tools import finite_inquiry as q
from tools import inquiry_policy as p
from tools import scoped_terms as t


def verify(journal, questions, objective, policy, *, horizon=2, budget=256):
    captured = p.context(journal, questions, objective, horizon, budget)
    if type(policy) is not p.Policy or policy.context != captured:
        raise t.Refused("stale contingent policy")
    observations.verify_estimate(journal, policy.estimate)
    if type(policy.expanded) is not int:
        raise t.Refused("malformed expansion count")
    if policy.estimate.posterior is None:
        if (policy.coverage, policy.expanded, policy.root) != ("no-supported-model", 0, None):
            raise t.Refused("unsupported model cannot supply a policy")
        return True
    spent = 0
    stop_id = t.Identity(p.PROFILE, captured, "stop")

    def replay(node, belief, remaining, path):
        nonlocal spent
        identity = t.Identity(p.PROFILE, q.fingerprint(captured, path, belief), "node")
        if type(node) is not p.Node or (node.identity, node.belief, node.remaining) != (identity, belief, remaining) or type(node.remaining) is not int:
            raise t.Refused("policy branch identity/belief/horizon mismatch")
        if any(type(x) is not bool for x in (node.expanded, node.complete)) or type(node.options) is not tuple or type(node.incumbents) is not tuple or any(type(x) is not F for x in (node.lower, node.upper)):
            raise t.Refused("malformed policy node")
        risks = tuple(sum((mass * loss for mass, loss in zip(belief.masses, row, strict=True)), F(0)) for row in objective.losses)
        stop_loss = min(risks)
        decision = q.Decision(q.fingerprint(belief, objective), stop_loss, tuple(x for x, risk in zip(objective.decisions.members, risks, strict=True) if risk == stop_loss))
        if type(node.stop) is not q.Decision or type(node.stop.expected_loss) is not F or type(node.stop.alternatives) is not tuple or node.stop != decision:
            raise t.Refused("policy stopping decision failed replay")
        should_expand = remaining > 0 and spent < budget
        if not should_expand:
            expected = (False, remaining == 0, stop_loss if remaining == 0 else F(0), stop_loss, (stop_id,))
            if node.options:
                raise t.Refused("terminal/cutoff node cannot contain searched options")
        else:
            spent += 1
            if len(node.options) != len(questions):
                raise t.Refused("policy omits a query alternative")
            lows, highs = [stop_loss], [stop_loss]
            complete = True
            for i, (question, option) in enumerate(zip(questions, node.options, strict=True)):
                if type(option) is not p.Option or option.question != question.identity or type(option.children) is not tuple or type(option.lower) is not F or type(option.upper) is not F:
                    raise t.Refused("invalid policy option")
                if type(option.inquiry) is not q.Inquiry or type(option.inquiry.cost) is not F or option.inquiry.cost != question.cost:
                    raise t.Refused("policy query cost mismatch")
                q.verify_inquiry(belief, question.kernel, objective, option.inquiry)
                if len(option.children) != len(option.inquiry.branches):
                    raise t.Refused("policy omits prospective outcome coverage")
                costs = []
                for j, (branch, child) in enumerate(zip(option.inquiry.branches, option.children, strict=True)):
                    if branch.posterior is None:
                        if child is not None:
                            raise t.Refused("zero-support branch invents a child belief")
                    else:
                        child_low, child_high, child_complete = replay(child, branch.posterior, remaining - 1, path + (i, j))
                        complete &= child_complete
                        costs.append((branch.mass * child_low, branch.mass * child_high))
                low = question.cost + sum((x[0] for x in costs), F(0))
                high = question.cost + sum((x[1] for x in costs), F(0))
                if (option.lower, option.upper) != (low, high):
                    raise t.Refused("contingent query cost bounds failed replay")
                lows.append(low)
                highs.append(high)
            upper = min(highs)
            choices = tuple(([stop_id] if stop_loss == upper else []) + [option.question for option in node.options if option.upper == upper])
            expected = (True, complete, min(lows), upper, choices)
        if (node.expanded, node.complete, node.lower, node.upper, node.incumbents) != expected:
            raise t.Refused("policy bounds, coverage or incumbent choices failed replay")
        return node.lower, node.upper, node.complete

    _, _, complete = replay(policy.root, policy.estimate.posterior, horizon, ())
    if policy.expanded != spent or policy.coverage != ("complete" if complete else "incomplete"):
        raise t.Refused("policy expansion/coverage failed replay")
    return True
