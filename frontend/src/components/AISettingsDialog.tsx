import React, { useState } from 'react';
import { Dialog } from '@headlessui/react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (tokens: { pb_token: string; plat_token: string }) => void;
}

export default function AISettingsDialog({ isOpen, onClose, onSubmit }: Props) {
  const [pbToken, setPbToken] = useState('0dPL9p66HeK2FZUORwP8YQ%3D%3D');
  const [platToken, setPlatToken] = useState('39WqZnPmcEx9IL82sNbiwQYl2Od0dGWnx%2F%2BnmxjBzQ%3D%3D');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      pb_token: pbToken,
      plat_token: platToken,
    });
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-md bg-white rounded-lg p-6">
          <Dialog.Title className="text-lg font-medium mb-4">
            AI点评设置
          </Dialog.Title>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                p-b Token
              </label>
              <input
                type="text"
                value={pbToken}
                onChange={(e) => setPbToken(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                p-lat Token
              </label>
              <input
                type="text"
                value={platToken}
                onChange={(e) => setPlatToken(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              />
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                确定
              </button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
