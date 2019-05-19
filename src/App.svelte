<script>
  import ItemList from "./ItemList.svelte";
  import Modal from "./Modal.svelte";
  import { AsyncSubject } from "rxjs";

  let show_settings_modal = false;
  let settings = { poesessid: "" };
  const settings_sub = new AsyncSubject();
  settings_sub.subscribe(console.log);

  $: settings_sub.next(settings);

  let items;
  export function set_item_list(new_items) {
    items = new_items;
  }

  function settings_modal_closed(event) {
    show_settings_modal = false;
    settings_sub.complete();
  }
</script>

<style>
  :global(body) {
    background-color: #000;
    background: gray url("teee.png") repeat 0 0;
    animation: shaper_slide 25s linear infinite;
    /* grid layout */
    display: grid;
    padding: 0.5em;
    grid-gap: 0.5em;
    grid:
      "menu menu menu menu" min-content
      "search items items items" 1fr
      / min-content 1fr;
  }
</style>

<button on:click={() => (show_settings_modal = true)}>Settings</button>

{#if show_settings_modal}
  <Modal on:close={settings_modal_closed}>
    <p slot="header">Settings</p>
    <span slot="closer">Save</span>
    <input type="text" bind:value={settings.poesessid} />
    <p>hi</p>
  </Modal>
{/if}
