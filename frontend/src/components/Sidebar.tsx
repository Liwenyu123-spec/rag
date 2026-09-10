import {
  Download,
  Image,
  Menu,
  MessageSquarePlus,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Settings2,
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
  onEditSystem,
  onExportSession,
  onWallpaper,
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
  onEditSystem?: () => void
  onExportSession?: () => void
  onWallpaper?: () => void
}) {
  const renderPanel = (forceOpen = false) => (
    <aside
      className={clsx(
        'sidebar-panel glass-panel flex h-full flex-col border-r',
        !forceOpen && collapsed
          ? 'w-0 overflow-hidden border-0 p-0 opacity-0'
          : 'w-[240px] opacity-100',
      )}
    >
      <div className="flex items-center justify-between gap-2 p-3">
        <button
          type="button"
          onClick={onNew}
          className="btn-motion btn-primary flex flex-1 items-center justify-center gap-2 rounded-[12px] bg-ds-blue px-3 py-2.5 text-sm font-medium text-white hover:bg-ds-blue-hover"
        >
          <MessageSquarePlus size={16} />
          新建对话
        </button>
        <button
          type="button"
          className="btn-motion btn-ghost hidden rounded-[12px] p-2 text-[var(--text-aux)] hover:text-[var(--text-main)] md:inline-flex"
          onClick={onToggleCollapse}
          title="折叠侧边栏"
        >
          <PanelLeftClose size={18} />
        </button>
        <button
          type="button"
          className="btn-motion btn-ghost inline-flex rounded-[12px] p-2 text-[var(--text-aux)] md:hidden"
          onClick={onCloseMobile}
        >
          <X size={18} />
        </button>
      </div>

      <div className="px-3 pb-2 text-[11px] font-normal tracking-wider text-aux">
        历史会话（本地已保存）
      </div>

      <div className="sidebar-scroll flex-1 space-y-1 overflow-y-auto px-2 pb-3">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={clsx(
              'session-item group flex items-center gap-1 rounded-[16px] px-2 py-2',
              s.id === activeId ? 'session-item-active' : '',
            )}
          >
            <button
              type="button"
              onClick={() => {
                onSelect(s.id)
                onCloseMobile()
              }}
              className="min-w-0 flex-1 truncate px-1 text-left text-[13px] font-normal text-[var(--text-main)]"
            >
              {s.title || '新对话'}
            </button>
            <button
              type="button"
              onClick={() => onDelete(s.id)}
              className="btn-motion rounded-[12px] p-1 text-[var(--text-aux)] opacity-0 transition group-hover:opacity-100 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      <div className="space-y-2 border-t border-white/10 p-3">
        {onWallpaper && (
          <button
            type="button"
            onClick={onWallpaper}
            className="btn-motion btn-ghost flex w-full items-center justify-center gap-2 rounded-[12px] border px-3 py-2 text-sm text-[var(--text-main)]"
          >
            <Image size={16} />
            聊天壁纸
          </button>
        )}
        {onEditSystem && (
          <button
            type="button"
            onClick={onEditSystem}
            className="btn-motion btn-ghost flex w-full items-center justify-center gap-2 rounded-[12px] border px-3 py-2 text-sm text-[var(--text-main)]"
          >
            <Settings2 size={16} />
            系统提示词
          </button>
        )}
        {onExportSession && (
          <button
            type="button"
            onClick={onExportSession}
            className="btn-motion btn-ghost flex w-full items-center justify-center gap-2 rounded-[12px] border px-3 py-2 text-sm text-[var(--text-main)]"
          >
            <Download size={16} />
            导出当前对话
          </button>
        )}
        <button
          type="button"
          onClick={onToggleDark}
          className="btn-motion btn-ghost flex w-full items-center justify-center gap-2 rounded-[12px] border px-3 py-2 text-sm text-[var(--text-main)]"
        >
          {dark ? <Sun size={16} /> : <Moon size={16} />}
          {dark ? '浅色主题' : '暗色主题'}
        </button>
      </div>
    </aside>
  )

  return (
    <>
      <div className="relative hidden h-full shrink-0 md:block">
        {renderPanel(false)}
        {collapsed && (
          <button
            type="button"
            onClick={onToggleCollapse}
            className="btn-motion btn-ghost absolute left-3 top-3 z-10 rounded-[12px] border p-2 text-[var(--text-aux)] hover:text-[var(--text-main)]"
            title="展开侧边栏"
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
      </div>

      <div
        className={clsx(
          'sidebar-overlay fixed inset-0 z-40 md:hidden',
          open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0',
        )}
      >
        <button
          type="button"
          className="absolute inset-0 bg-black/50"
          aria-label="关闭侧边栏"
          onClick={onCloseMobile}
        />
        <div
          className={clsx(
            'sidebar-drawer absolute left-0 top-0 h-full',
            open ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          {renderPanel(true)}
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
      className="btn-motion btn-ghost inline-flex rounded-[12px] border p-2 text-[var(--text-aux)] md:hidden"
    >
      <Menu size={18} />
    </button>
  )
}
