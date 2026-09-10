import {
  Menu,
  MessageSquarePlus,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  Trash2,
  X,
} from 'lucide-react'
import clsx from 'clsx'
import type { Session } from '../types'

export function Sidebar({
  open,
  collapsed,
  sessions,
  activeId,
  dark,
  onToggleDark,
  onSelect,
  onNew,
  onDelete,
  onCloseMobile,
  onToggleCollapse,
}: {
  open: boolean
  collapsed: boolean
  sessions: Session[]
  activeId: string
  dark: boolean
  onToggleDark: () => void
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
  onCloseMobile: () => void
  onToggleCollapse: () => void
}) {
  const renderPanel = (forceOpen = false) => (
    <aside
      className={clsx(
        'flex h-full flex-col border-r border-ds-border bg-ds-subtle transition-all duration-200',
        !forceOpen && collapsed
          ? 'w-0 overflow-hidden border-0 p-0 opacity-0'
          : 'w-[240px] opacity-100',
      )}
    >
      <div className="flex items-center justify-between gap-2 p-3">
        <button
          type="button"
          onClick={onNew}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-ds-blue px-3 py-2.5 text-sm font-medium text-white transition hover:bg-ds-blue-hover"
        >
          <MessageSquarePlus size={16} />
          新建对话
        </button>
        <button
          type="button"
          className="hidden rounded-lg p-2 text-ds-muted transition hover:bg-black/5 hover:text-ds-text md:inline-flex dark:hover:bg-white/5"
          onClick={onToggleCollapse}
          title="折叠侧边栏"
        >
          <PanelLeftClose size={18} />
        </button>
        <button
          type="button"
          className="inline-flex rounded-lg p-2 text-ds-muted md:hidden"
          onClick={onCloseMobile}
        >
          <X size={18} />
        </button>
      </div>

      <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-ds-muted">
        历史会话
      </div>

      <div className="flex-1 space-y-1 overflow-y-auto px-2 pb-3">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={clsx(
              'group flex items-center gap-1 rounded-xl px-2 py-2 transition',
              s.id === activeId
                ? 'bg-white shadow-sm dark:bg-white/10'
                : 'hover:bg-white/70 dark:hover:bg-white/5',
            )}
          >
            <button
              type="button"
              onClick={() => {
                onSelect(s.id)
                onCloseMobile()
              }}
              className="min-w-0 flex-1 truncate px-1 text-left text-[13px] text-ds-text"
            >
              {s.title || '新对话'}
            </button>
            <button
              type="button"
              onClick={() => onDelete(s.id)}
              className="rounded-md p-1 text-ds-muted opacity-0 transition group-hover:opacity-100 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      <div className="border-t border-ds-border p-3">
        <button
          type="button"
          onClick={onToggleDark}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-ds-border bg-ds-bg px-3 py-2 text-sm text-ds-text transition hover:border-ds-blue/40"
        >
          {dark ? <Sun size={16} /> : <Moon size={16} />}
          {dark ? '浅色主题' : '暗色主题'}
        </button>
      </div>
    </aside>
  )

  return (
    <>
      {/* Desktop */}
      <div className="relative hidden h-full shrink-0 md:block">
        {panel}
        {collapsed && (
          <button
            type="button"
            onClick={onToggleCollapse}
            className="absolute left-3 top-3 z-10 rounded-lg border border-ds-border bg-ds-bg p-2 text-ds-muted shadow-sm transition hover:text-ds-text"
            title="展开侧边栏"
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
      </div>

      {/* Mobile drawer */}
      <div
        className={clsx(
          'fixed inset-0 z-40 md:hidden transition-opacity duration-200',
          open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0',
        )}
      >
        <button
          type="button"
          className="absolute inset-0 bg-black/40"
          aria-label="关闭侧边栏"
          onClick={onCloseMobile}
        />
        <div
          className={clsx(
            'absolute left-0 top-0 h-full transition-transform duration-200',
            open ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className="h-full w-[240px] [&_aside]:w-[240px] [&_aside]:opacity-100">
            {panel}
          </div>
        </div>
      </div>
    </>
  )
}

export function MobileMenuButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex rounded-lg border border-ds-border bg-ds-bg p-2 text-ds-muted md:hidden"
    >
      <Menu size={18} />
    </button>
  )
}
