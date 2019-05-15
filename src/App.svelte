<script>
  import Thing from "./Thing.svelte";
  import { from } from "rxjs";
  import { ajax } from "rxjs/ajax";
  import { pluck, startWith } from "rxjs/operators";

  const things2 = from([
    { id: 1, response: { login: "a" } },
    { id: 2, response: { login: "b" } },
    { id: 3, response: { login: "c" } },
    { id: 4, response: { login: "d" } },
    { id: 5, response: { login: "e" } }
  ]).pipe(
    pluck("response"),
    startWith([])
  );

  // const values = things.pipe(startWith([]));

  const things = ajax(`https://api.github.com/users?per_page=5`).pipe(
    pluck("response"),
    startWith([])
  );
</script>

{#each $things2 as t}
  <Thing {...t} />
  <p>{t}</p>
{/each}

<!-- {#each things as thing (thing.id)}
  <Thing value={thing.value} />
{/each} -->

<!-- {#each $values as t (t.id)}
  <div>{t}</div>
  <Thing value={t.value} />
{/each} -->
