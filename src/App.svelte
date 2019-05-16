<script>
  import Thing from "./Thing.svelte";
  import { from } from "rxjs";
  import { scan, tap } from "rxjs/operators";

  const things = from([
    { id: 1, value: 1 },
    { id: 2, value: 2 },
    { id: 3, value: 3 },
    { id: 4, value: 4 }
  ]).pipe(
    tap(console.log),
    scan((a, c) => [...a, c], [])
  );
</script>

{#each $things as t (t.id)}
  <Thing {...t} />
{/each}

<!-- {#each things as thing (thing.id)}
  <Thing value={thing.value} />
{/each} -->

<!-- {#each $values as t (t.id)}
  <div>{t}</div>
  <Thing value={t.value} />
{/each} -->
