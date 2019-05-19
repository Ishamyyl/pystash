<script>
  import Item from "./Item.svelte";
  export let items = [];
</script>

<style>
  div {
    grid-area: items;

    /* grid layout */
    display: grid;
    grid-template-rows: 100px;
    grid-auto-flow: row;
  }
</style>

<div>
  {#each items as t}
    <Item {...t} />
  {/each}
</div>
